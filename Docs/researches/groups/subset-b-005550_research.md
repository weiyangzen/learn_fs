# subset-b-005550 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vhost.h -->
# sources/distributed-fs/ceph-client/drivers/vhost/vhost.h

## Purpose
`vhost.h` is the private shared interface for Linux vhost device implementations. It defines the in-kernel representation of vhost devices, virtqueues, workers, polling hooks, logging state, IOTLB metadata, and feature helpers used by concrete backends such as vhost-vsock, vhost-net, and vhost-scsi.

## Important APIs, types, and functions
Key types are `struct vhost_dev`, `struct vhost_virtqueue`, `struct vhost_worker`, `struct vhost_poll`, `struct vhost_work`, `struct vhost_vring_call`, and `struct vhost_msg_node`. The header declares lifecycle APIs (`vhost_dev_init`, `vhost_dev_set_owner`, `vhost_dev_stop`, `vhost_dev_cleanup`, `vhost_dev_reset_owner`), ioctl dispatch (`vhost_dev_ioctl`, `vhost_vring_ioctl`, `vhost_worker_ioctl`), queue traversal/completion (`vhost_get_vq_desc`, `vhost_get_vq_desc_n`, `vhost_add_used*`, `vhost_signal`), polling (`vhost_poll_*`), IOTLB setup (`vhost_init_device_iotlb`), and character-device helpers (`vhost_chr_*`). Inline helpers cover backend private data, negotiated features, endian conversion, and feature-array construction.

## Control flow
Backends allocate `vhost_virtqueue` arrays, call `vhost_dev_init`, set ownership from userspace, configure rings through ioctls, then start queue processing. Queue kicks enter `vhost_poll`, enqueue `vhost_work`, parse descriptors, copy data, publish used elements, and signal eventfds. Device shutdown clears backend pointers, flushes queued work, tears down IOTLB/logging state, and releases owner resources.

## State and persistence
State is entirely kernel runtime state: owner `mm`, queue ring pointers, eventfd contexts, per-vq indices, feature bits, IOTLB pointers, logging buffers, worker xarray, pending/read message lists, and backend-private pointers. Nothing persists across device close. Synchronization is explicit through device/vq mutexes, spinlocks for IOTLB, RCU worker pointers, and wait queues.

## Dependencies and integration points
The header depends on eventfd, poll, uio, virtio ring/config, xarray, irq bypass, vhost IOTLB, and Linux feature-bit helpers. It integrates with userspace vhost ioctls, virtio feature negotiation, eventfd notifications, dirty-page logging, memory translation, and backend-specific transport drivers.

## Risks and test signals
Risks concentrate around user-provided ring pointers, descriptor bounds, endian mode, feature mismatch, worker swaps, IOTLB permissions, and eventfd lifetime. Test signals include vhost ioctl coverage, malformed descriptor chains, feature negotiation matrices, cross-endian legacy tests, IOTLB map/unmap races, dirty logging, worker attach/detach, and backend teardown while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vhost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vringh.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/vringh.c

## Purpose
`vringh.c` implements exported helpers for the host side of a virtio split ring. It provides descriptor acquisition, iovec construction, buffer copying, used-ring completion, and notification decisions for rings backed by userspace memory, kernel memory, or vhost-IOTLB translated memory.

## Important APIs, types, and functions
Public exports include `vringh_init_user`, `vringh_getdesc_user`, `vringh_iov_pull_user`, `vringh_iov_push_user`, `vringh_complete_user`, `vringh_need_notify_user`, their `_kern` equivalents, and IOTLB variants under `CONFIG_VHOST_IOTLB`. Shared internals include `__vringh_get_head`, `__vringh_iov`, `__vringh_complete`, `__vringh_need_notify`, `__vringh_notify_enable`, `range_check`, `move_to_indirect`, `resize_iovec`, and the IOTLB translator/copy helpers.

## Control flow
Initialization validates ring size and records endian/event-index/barrier mode. Descriptor consumption reads the avail index, applies the virtio read barrier, fetches the next head, validates descriptor chains, follows one level of indirect descriptors, enforces readable-before-writable ordering, and fills read/write iov arrays. Data movement advances iov cursors as bytes are copied. Completion writes used elements, issues a write barrier, updates used index, accumulates completion count, and later decides whether to notify based on flags or event index.

## State and persistence
The persistent runtime state lives in `struct vringh`: ring pointers, last avail/used indices, completed count, feature-derived booleans, and optional IOTLB pointers/lock. `vringh_iov`/`vringh_kiov` retain cursor state and may allocate larger vectors. There is no storage persistence.

## Dependencies and integration points
The file depends on virtio ring definitions, Linux uaccess, iov iterators, slab allocation, memory barriers, and optional vhost IOTLB maps. It exports symbols consumed by vhost and other virtio host-side code that needs common split-ring mechanics without duplicating descriptor parsing.

## Risks and test signals
High-risk areas are descriptor loops, invalid indirect tables, address wrapping, partial range translations, user access faults, IOTLB permission errors, ring wraparound, and event-index memory ordering. Test signals should include fuzzed descriptor chains, indirect descriptors crossing ranges, mixed readable/writable ordering, ENOBUFS translation slicing, user copy fault injection, ring size validation, and notification behavior with and without `VIRTIO_RING_F_EVENT_IDX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vringh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vsock.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/vsock.c

## Purpose
`vsock.c` implements the vhost transport for AF_VSOCK. It exposes `/dev/vhost-vsock`, binds a guest CID to a vhost device, moves packets between virtio-vsock queues and the host vsock core, and provides host-to-guest and guest-to-host transport operations.

## Important APIs, types, and functions
The central type is `struct vhost_vsock`, containing `struct vhost_dev`, two virtqueues, namespace state, CID hash linkage, a host-to-guest SKB queue, send work, reply accounting, and negotiated seqpacket state. Important functions are `vhost_transport_send_pkt`, `vhost_transport_do_send_pkt`, `vhost_vsock_handle_tx_kick`, `vhost_vsock_start`, `vhost_vsock_stop`, `vhost_vsock_set_cid`, `vhost_vsock_set_features`, `vhost_vsock_dev_ioctl`, open/release handlers, and module init/exit registration.

## Control flow
Open allocates a large `vhost_vsock`, initializes two queues and vhost core state, and stores it in `file->private_data`. Userspace sets owner/rings/features/CID through ioctls and starts the device. Host-to-guest packets are queued by CID lookup, then `send_pkt_work` drains SKBs into RX virtqueue buffers. Guest-to-host packets arrive on TX kicks, are copied from descriptors into SKBs, address-validated, and delivered to `virtio_transport_recv_pkt`. Release removes the CID from the global hash, waits for RCU readers, resets orphaned sockets, stops/flushed vhost, purges SKBs, and frees resources.

## State and persistence
Runtime state includes per-open queue configuration, CID hash membership, network namespace reference, pending SKBs, `queued_replies`, and negotiated features. It does not persist beyond device lifetime. Mutexes protect vhost/vq changes; a global mutex plus RCU protects CID lookup.

## Dependencies and integration points
The file integrates with vhost core, virtio-vsock packet helpers, AF_VSOCK transport registration, miscdevice operations, network namespaces, eventfd-backed virtqueues, and optional vhost IOTLB backend feature negotiation.

## Risks and test signals
Risks include CID collisions across namespaces, bad packet lengths, malformed descriptor direction, reply-queue starvation, partial RX buffer splitting for seqpacket EOM/EOR flags, teardown races with socket lookup, and feature/IOTLB mismatch. Test signals include vhost-vsock ioctl tests, namespace-isolated CIDs, stream and seqpacket traffic, oversized packet splitting, queue exhaustion/restart, orphan reset on release, and malformed guest descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/Kconfig

## Purpose
This Kconfig file defines the `Graphics support` menu and wires legacy video, framebuffer, console, backlight, logo, EDID, aperture, HDMI, and helper options into the kernel configuration tree.

## Important APIs, types, and functions
It is declarative Kconfig rather than C code. Important symbols include `APERTURE_HELPERS`, `SCREEN_INFO`, `STI_CORE`, `VIDEO`, `HAVE_FB_ATMEL`, `VGASTATE`, `VIDEOMODE_HELPERS`, `HDMI`, and `FIRMWARE_EDID`. It sources submenus for auxdisplay, AGP, VGA, GPU, DRM, framebuffer devices, backlight devices, console, logo, and GPU tracing.

## Control flow
Configuration visibility is gated primarily by `HAS_IOMEM` and `VT`. If I/O memory is available, the file exposes GPU/DRM/fbdev/backlight and low-level video helpers. Firmware EDID is exposed outside `HAS_IOMEM` but depends on EFI generic stub or x86. Console and logo submenus are included only when their owning subsystems are configured.

## State and persistence
The file contributes build-time state only. Selected symbols persist in `.config` and drive object inclusion through Makefiles and preprocessor conditionals.

## Dependencies and integration points
It is the parent for many graphics subsystems. `APERTURE_HELPERS` maps to `drivers/video/aperture.c`; `VIDEO` maps to video command-line helpers; `VIDEOMODE_HELPERS` selects display timing conversions; `source "drivers/video/backlight/Kconfig"` integrates the backlight/LCD driver menu.

## Risks and test signals
Risks are dependency mistakes that expose drivers on unsupported platforms or hide required helpers from DRM/fbdev users. Test signals include `allyesconfig`, `allmodconfig`, architecture-specific builds without `HAS_IOMEM`, x86/EFI firmware EDID combinations, and randconfig coverage for sourced submenu reachability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/Makefile

## Purpose
This Makefile maps top-level video Kconfig symbols to built objects and subdirectories. It is the build glue for aperture helpers, screen info, STI, VGA state, command-line video helpers, HDMI, console, logo, backlight, fbdev, and videomode helpers.

## Important APIs, types, and functions
The file uses standard kbuild variables: `obj-$(CONFIG_...)`, composite object lists such as `screen_info-y`, and conditional `ifeq ($(CONFIG_OF),y)` inclusion. Notable mappings include `CONFIG_APERTURE_HELPERS -> aperture.o`, `CONFIG_VIDEO -> cmdline.o nomodeset.o`, unconditional descent into `backlight/` and `fbdev/`, and `CONFIG_VIDEOMODE_HELPERS` objects.

## Control flow
Kbuild evaluates config variables, adds matching objects or directories, and descends into subdirectories as needed. `backlight/` and `fbdev/` are always visited so their own Makefiles can decide object inclusion from their local symbols.

## State and persistence
The file has no runtime state. Its state is build graph state derived from `.config`.

## Dependencies and integration points
It integrates the symbols declared in `drivers/video/Kconfig` with compiled C sources. The `CONFIG_OF` branch adds device-tree timing conversion helpers only when OF support is built.

## Risks and test signals
Risks are stale symbol/object names, unconditional subdirectory descent interacting with missing dependencies, and OF helper omissions. Test signals include kbuild for minimal configs, `CONFIG_OF=n` with `VIDEOMODE_HELPERS=y`, modular backlight/fbdev builds, and `make W=1` for orphaned objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/aperture.c -->
# sources/distributed-fs/ceph-client/drivers/video/aperture.c

## Purpose
`aperture.c` manages ownership of firmware-provided framebuffer memory ranges so native graphics drivers can evict generic framebuffer drivers cleanly before binding hardware.

## Important APIs, types, and functions
The internal `struct aperture_range` records owner device, physical base/size, list linkage, and detach callback. Public exports are `devm_aperture_acquire_for_platform_device`, `aperture_remove_conflicting_devices`, `__aperture_remove_legacy_vga_devices`, and `aperture_remove_conflicting_pci_devices`. Internal helpers include `overlap`, `devm_aperture_acquire`, `aperture_detach_platform_device`, and `aperture_detach_devices`.

## Control flow
Generic platform framebuffer drivers acquire an aperture during probe. Native drivers later call a remove-conflicting helper. That disables future sysfb registration, walks registered apertures under a mutex, detects overlapping ranges, removes them from the list, marks the range detached, and invokes the detach callback, currently `platform_device_unregister`. PCI callers iterate memory BARs and additionally remove legacy VGA resources for the default VGA adapter.

## State and persistence
State is the global `apertures` list protected by `apertures_lock`. Entries are device-managed allocations and are removed automatically when the owning device goes away, unless already detached. No state persists across boot.

## Dependencies and integration points
The file integrates with sysfb, platform devices, PCI BAR resources, VGA arbitration, legacy VGA framebuffer constants, and devres-managed lifetime. Graphics drivers call it before hardware initialization to avoid two drivers touching the same framebuffer.

## Risks and test signals
Risks include overlap arithmetic overflow (`base + size`), detach callback while holding the aperture mutex, stale device-managed release after forced detach, accidental removal of a non-conflicting device, and VGA console interactions. Test signals include sysfb handoff from EFI/VESA/simplefb to DRM, PCI default VGA removal, non-overlapping apertures, overlapping partial ranges, hot-unplug capable platform framebuffer drivers, and repeated acquire/remove sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/aperture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/88pm860x_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/88pm860x_bl.c

## Purpose
This platform driver controls Marvell 88PM8606 WLED backlight outputs through the 88PM860x MFD register interface.

## Important APIs, types, and functions
`struct pm860x_backlight_data` stores chip/client pointers, selected port, PWM/current settings, current brightness, and register addresses supplied as platform resources. Key functions are `backlight_power_set`, `pm860x_backlight_set`, `pm860x_backlight_update_status`, `pm860x_backlight_get_brightness`, optional `pm860x_backlight_dt_init`, and `pm860x_backlight_probe`. The backlight ops support suspend/resume and hardware brightness readback.

## Control flow
Probe resolves register resources named `duty cycle`, `always on`, and `current`, derives the backlight name from `pdev->id`, loads DT or platform data for current/PWM settings, registers a raw backlight, reads current duty cycle, and updates hardware. Brightness updates enable the WLED oscillator before writing duty when nonzero, program current/PWM on first transition from off, set or clear the always-on bit for full brightness, and disable the oscillator when brightness becomes zero.

## State and persistence
Driver state is device-managed and runtime-only. Hardware state persists in PMIC registers until changed or reset. `current_brightness` is cached to detect off-to-on transitions.

## Dependencies and integration points
It depends on the 88PM860x MFD core, platform resources, optional OF child nodes under `backlights`, and the backlight core.

## Risks and test signals
Risks include missing named resources, invalid platform ID/port, DT child-name mismatches, partial programming after register failures, and hardware state drift if cached brightness differs from duty. Test signals include probing all three ports, DT and legacy platform data, zero/full/intermediate brightness transitions, suspend/resume, and injected PMIC register failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/88pm860x_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/Kconfig

## Purpose
This Kconfig file defines the LCD and backlight support menu, including the generic LCD/backlight class devices and a broad set of panel, PMIC, GPIO, PWM, LED, platform, and I2C backlight drivers.

## Important APIs, types, and functions
Important framework symbols are `LCD_CLASS_DEVICE` and `BACKLIGHT_CLASS_DEVICE`. The listed work item drivers map to symbols such as `LCD_AMS369FG06`, `BACKLIGHT_AW99706`, `BACKLIGHT_APPLE`, `BACKLIGHT_APPLE_DWI`, `BACKLIGHT_ADP5520`, `BACKLIGHT_ADP8860`, `BACKLIGHT_ADP8870`, `BACKLIGHT_88PM860X`, `BACKLIGHT_AAT2870`, `BACKLIGHT_AS3711`, `BACKLIGHT_BD6107`, and `BACKLIGHT_ARCXCNN`. Many entries add `depends on` subsystem constraints and `select` helper libraries such as `REGMAP_I2C`, `NEW_LEDS`, or `LEDS_CLASS`.

## Control flow
LCD panel options are visible only under `LCD_CLASS_DEVICE`; backlight options are visible only under `BACKLIGHT_CLASS_DEVICE`. Per-driver dependencies constrain platform buses, MFD parents, I2C/SPI, ACPI, OF, GPIO, PWM, and architecture support. Kconfig selections then drive the local Makefile.

## State and persistence
The file contributes build-time configuration state in `.config`; no runtime state exists.

## Dependencies and integration points
It integrates low-level display control with the Linux driver model by ensuring core class support and bus/helper dependencies are available before individual drivers compile.

## Risks and test signals
Risks are under-specified dependencies, missing selects for helper APIs, stale help text/module names, and options visible on impossible hardware. Test signals include randconfig builds, `COMPILE_TEST` coverage, module builds for each option, and dependency audits against each driver's includes and API calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/Makefile

## Purpose
This Makefile maps LCD and backlight Kconfig symbols to their corresponding driver objects in `drivers/video/backlight`.

## Important APIs, types, and functions
It uses kbuild `obj-$(CONFIG_SYMBOL) += object.o` lines. Relevant mappings include `CONFIG_LCD_AMS369FG06 -> ams369fg06.o`, `CONFIG_BACKLIGHT_88PM860X -> 88pm860x_bl.o`, `CONFIG_BACKLIGHT_AAT2870 -> aat2870_bl.o`, `CONFIG_BACKLIGHT_ADP5520 -> adp5520_bl.o`, `CONFIG_BACKLIGHT_ADP8860 -> adp8860_bl.o`, `CONFIG_BACKLIGHT_ADP8870 -> adp8870_bl.o`, `CONFIG_BACKLIGHT_APPLE -> apple_bl.o`, `CONFIG_BACKLIGHT_APPLE_DWI -> apple_dwi_bl.o`, `CONFIG_BACKLIGHT_ARCXCNN -> arcxcnn_bl.o`, `CONFIG_BACKLIGHT_AS3711 -> as3711_bl.o`, `CONFIG_BACKLIGHT_AW99706 -> aw99706.o`, `CONFIG_BACKLIGHT_CLASS_DEVICE -> backlight.o`, and `CONFIG_BACKLIGHT_BD6107 -> bd6107.o`.

## Control flow
Kbuild includes objects as built-in or modules according to each symbol value. The generic `backlight.o` class core is only built when `BACKLIGHT_CLASS_DEVICE` is enabled.

## State and persistence
Only build graph state exists. Runtime behavior is controlled by the resulting objects and their module metadata.

## Dependencies and integration points
The Makefile is the bridge from `backlight/Kconfig` symbols to C sources. It must remain synchronized with config names, module aliases, and file renames.

## Risks and test signals
Risks include missing object mappings, typos in symbol names, and building a driver without its framework object. Test signals include enabling each listed config as `m` and `y`, `make modules`, and comparing Kconfig entries against Makefile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/aat2870_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/aat2870_bl.c

## Purpose
This platform driver controls the AnalogicTech AAT2870 backlight block through callbacks exposed by the AAT2870 MFD core.

## Important APIs, types, and functions
`struct aat2870_bl_driver_data` stores the platform device, backlight device, channel mask, max current, and cached brightness. Key functions are `aat2870_brightness`, `aat2870_bl_enable`, `aat2870_bl_disable`, `aat2870_bl_update_status`, `aat2870_bl_probe`, and `aat2870_bl_remove`.

## Control flow
Probe requires platform data and the expected platform ID, registers a raw backlight, applies channel/current/max-brightness defaults, initializes brightness to max, and calls update. Updates validate brightness, scale the requested backlight brightness into the chip current register, write `AAT2870_BLM`, disable all channels at zero, and enable configured channels on transition from off to nonzero. Remove forces power off and brightness zero.

## State and persistence
Runtime state is device-managed, with a cached brightness used for transition decisions. Hardware register state persists until changed by the MFD or reset.

## Dependencies and integration points
It depends on `MFD_AAT2870_CORE`, platform data, parent device driver data, and the backlight core. The MFD provides the actual `write` operation.

## Risks and test signals
Risks include no platform data, invalid platform ID, scaling divide assumptions, parent driver-data mismatch, and inconsistent hardware state after failed writes. Test signals include default and explicit platform data, all-channel and subset-channel masks, brightness 0/max/intermediate transitions, remove path power-off, and MFD write failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/aat2870_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp5520_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/adp5520_bl.c

## Purpose
This platform driver controls ADP5520/ADP5501 WLED backlights behind the ADP5520 MFD and optionally exposes ambient-light-zone tuning registers through sysfs.

## Important APIs, types, and functions
`struct adp5520_bl` stores the parent MFD device, platform data, a sysfs lock, cached daylight maximum, device id, and current brightness. Main functions are `adp5520_bl_set`, `adp5520_bl_get_brightness`, `adp5520_bl_setup`, `adp5520_show/store`, `adp5520_bl_probe`, `adp5520_bl_remove`, and PM suspend/resume handlers. Backlight ops implement update and get brightness.

## Control flow
Probe requires platform data, registers a raw backlight, creates ALS sysfs attributes when ambient sensing is enabled, programs daylight/office/dark max and dim thresholds, configures comparator/fade/control registers, enables the backlight in dim mode, and updates brightness. Manual brightness below max disables auto ambient adjustment and writes `DAYLIGHT_MAX`; max brightness restores cached daylight max and enables auto adjustment.

## State and persistence
The cache tracks daylight max while sysfs can mutate ALS registers. `current_brightness` tracks dim transitions. Hardware register settings remain in the PMIC until reprogrammed or reset.

## Dependencies and integration points
It depends on the ADP5520 MFD helper API, platform data, the backlight class, sysfs attributes, and PM callbacks.

## Risks and test signals
Risks include OR-accumulated register errors hiding the first failure source, sysfs values without range validation, missing platform data, and cache/register divergence for daylight max. Test signals include ALS enabled/disabled probe paths, sysfs read/write for all six attributes, suspend/resume, brightness zero/manual/max behavior, and MFD read/write fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp5520_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp8860_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/adp8860_bl.c

## Purpose
This I2C driver controls ADP8860/ADP8861/ADP8863 WLED backlights and optional independent current-sink LEDs.

## Important APIs, types, and functions
`struct adp8860_bl` stores I2C client, backlight, optional LED array, platform data, lock, cached ALS max, revision, brightness, and feature flags. `struct adp8860_led` wraps LED classdev plus deferred I2C work. Main routines are SMBus helpers, `adp8860_led_probe/remove`, `adp8860_bl_set`, `adp8860_bl_setup`, ALS sysfs show/store functions, `adp8860_probe/remove`, and PM suspend/resume.

## Control flow
Probe validates SMBus byte-data support and platform data, reads manufacturer/revision, derives supported ambient/gdwn behavior, registers the backlight, optionally creates ALS sysfs attributes, initializes backlight sink assignments and comparator thresholds, enables standby/backlight/dim bits, updates brightness, and optionally registers independent LEDs. LED brightness writes run in workqueue context because I2C can sleep.

## State and persistence
Driver state tracks current brightness, cached daylight max, LED objects, feature flags, and register writes. Hardware ALS/backlight/LED registers persist until suspend/remove or reset.

## Dependencies and integration points
It depends on I2C SMBus, platform data definitions, the backlight core, LED class, workqueues, and PM. Kconfig selects LED support for this driver.

## Risks and test signals
Risks include platform-data-only configuration, LED/backlight sink assignment conflicts, partial LED registration unwind, unchecked return from optional `adp8860_led_probe`, sysfs writes with limited validation, and device variant feature differences. Test signals include all supported IDs, ALS on/off, LED registration conflicts, brightness 0/max/manual transitions, ambient zone sysfs, suspend/resume, and SMBus failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp8860_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp8870_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/adp8870_bl.c

## Purpose
This I2C driver supports ADP8870 WLED backlight control, five-zone ambient-light adjustment, PWM assignment, and optional independent LED sink registration.

## Important APIs, types, and functions
`struct adp8870_bl` contains client, backlight, optional LED array, platform data, lock, cached daylight max, revision, and current brightness. `struct adp8870_led` represents LED class devices with workqueue-backed I2C updates. Key functions include `adp8870_read/write/set_bits/clr_bits`, `adp8870_led_probe/remove`, `adp8870_bl_set`, `adp8870_bl_setup`, ALS sysfs accessors, `adp8870_probe/remove`, and PM callbacks.

## Control flow
Probe validates SMBus byte-data, platform data, and manufacturer ID, registers a raw backlight, optionally creates ALS sysfs attributes, programs sink selection, PWM selection, five brightness/dim levels, trip/hysteresis thresholds, comparator control, fade law/rates, and enables standby/backlight/dim mode. Brightness below max disables comparator auto mode and writes manual max current; max restores cached daylight max and reenables auto mode. Optional LEDs are registered after backlight setup.

## State and persistence
Runtime state records cached brightness and daylight max plus optional LED state. Hardware register programming persists until removal, suspend, or chip reset. LED brightness updates are deferred through work structs.

## Dependencies and integration points
It integrates with I2C SMBus, backlight core, LED class, platform data, sysfs, and PM. It exposes module/device tables for I2C matching.

## Risks and test signals
Risks include large platform-data surface, unhandled return from optional LED probe, sink conflicts, sysfs writes without strong range checks, and revision-specific `GDWN_DIS` behavior. Test signals include manufacturer mismatch, five ALS zones, PWM assignment, LED conflict/unwind, brightness 0/manual/max, suspend/resume, and I2C fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/adp8870_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ams369fg06.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ams369fg06.c

## Purpose
This SPI driver controls the Samsung AMS369FG06 AMOLED panel, registering both an LCD device for panel power and a backlight device for gamma/brightness selection.

## Important APIs, types, and functions
`struct ams369fg06` stores device, SPI, power state, LCD/backlight devices, and platform callbacks. Static command sequences describe display on/off, standby, and initialization. Important functions include `ams369fg06_spi_write_byte`, `ams369fg06_panel_send_sequence`, gamma control helpers, `ams369fg06_ldi_init/enable/disable`, `ams369fg06_power_on/off`, LCD ops, backlight update, probe/remove, PM, and shutdown.

## Control flow
Probe sets 16-bit SPI mode, requires platform data, registers LCD and backlight devices, sets default brightness, and powers the panel on if it was not already enabled by firmware. Power-on calls optional platform power, reset, sends initialization and display-on sequences, then applies gamma for current brightness. Backlight brightness maps the 0-255 range into one of five fixed gamma tables.

## State and persistence
The cached `power` tracks LCD power mode. Brightness is stored in the backlight core; hardware gamma and panel registers persist until rewritten or power-cycled.

## Dependencies and integration points
It depends on SPI, LCD class, backlight class, platform-provided reset/power callbacks and timing delays, and PM callbacks.

## Risks and test signals
Risks include mandatory platform data, no DT binding in this file, command sequence fragility, brightness-to-gamma coarse mapping, SPI transfer failures, and power sequencing delays. Test signals include cold boot with panel on/off, suspend/resume, shutdown, invalid brightness, missing reset callback, SPI setup failure, and visual/gamma validation at each brightness band.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ams369fg06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/apple_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/apple_bl.c

## Purpose
This platform driver provides vendor backlight control for Intel-based Apple systems by triggering firmware SMI commands through legacy I/O ports.

## Important APIs, types, and functions
`struct hw_data` describes I/O resource range, backlight ops, and raw set callback. Two implementations exist: Intel chipset ports `0xb2/0xb3` and Nvidia chipset ports `0x52e/0x52f`. Key functions are chipset get/set/update helpers, `apple_bl_probe`, `apple_bl_remove`, and module init/exit. ACPI matching uses `APP0002`.

## Control flow
Module init first asks ACPI video which backlight provider should be used and registers only for vendor backlight mode. Probe discovers the PCI host bridge vendor, selects the chipset implementation, tests whether brightness SMI responds, reserves the I/O port range, registers a platform-type backlight with max 15, reads current brightness, and updates status. Remove unregisters and releases the I/O region.

## State and persistence
Global `apple_backlight_device` and `hw_data` hold runtime state. Actual brightness is firmware/platform state exposed through port-triggered SMI side effects.

## Dependencies and integration points
It depends on x86 ACPI, PCI host bridge detection, I/O port access, ACPI video backlight arbitration, and the backlight core.

## Risks and test signals
Risks include SMI side effects, firmware non-response under EFI, global state assumptions, conflict with apple-gmux or ACPI video, and direct port I/O. Test signals include machines with Intel and Nvidia chipsets, `acpi_backlight=` mode variations, I/O region conflict, get/set brightness 0-15, suspend/resume through `BL_CORE_SUSPENDRESUME`, and non-Apple ACPI false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/apple_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/apple_dwi_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/apple_dwi_bl.c

## Purpose
This platform driver controls Apple DWI two-wire-interface backlight controllers through memory-mapped command and control registers, primarily for Apple SoC systems.

## Important APIs, types, and functions
`struct apple_dwi_bl` stores the MMIO base. Important routines are `dwi_bl_update_status`, `dwi_bl_get_brightness`, and `dwi_bl_probe`. Register definitions cover command type/data fields and control send bits, including `SEND4` for Apple A9 and later. The OF compatible is `apple,dwi-bl`.

## Control flow
Probe allocates state, ioremaps the first platform resource, registers a platform-type linear backlight with max 2047, and seeds brightness from the current command register. Brightness updates build a set-brightness command with `FIELD_PREP`, write it to `DWI_BL_CMD`, and trigger transmission by writing the combined send bits to `DWI_BL_CTL`.

## State and persistence
The driver keeps only the MMIO base pointer. Brightness state is read back from the command register and mirrored by the backlight core. Hardware state persists in controller registers.

## Dependencies and integration points
It depends on platform resources, OF matching, MMIO accessors, bitfield helpers, and the backlight core.

## Risks and test signals
Risks include applying `SEND4` on older variants if incompatible, no explicit range clamp beyond backlight core properties, lack of runtime PM/disable path, and command-register readback not necessarily reflecting panel output. Test signals include OF probe, MMIO resource failure, brightness 0/max/intermediate writes, suspend/resume via core option, and hardware validation on pre-A9 and A9+ controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/apple_dwi_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/arcxcnn_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/arcxcnn_bl.c

## Purpose
This I2C driver controls ArcticSand ARCxCnnn-family LED backlight controllers, currently matching `arc2c0608`, with 12-bit brightness and configurable LED-string/current behavior.

## Important APIs, types, and functions
`struct arcxcnn_platform_data` captures name, initial brightness, LED enables, fade/config/dimming/filter/trim settings. `struct arcxcnn` stores client, backlight, device, and platform data. Key functions are `arcxcnn_update_field`, `arcxcnn_set_brightness`, `arcxcnn_bl_update_status`, `arcxcnn_backlight_register`, `arcxcnn_parse_dt`, `arcxcnn_probe`, and `arcxcnn_remove`.

## Control flow
Probe checks SMBus byte-data, allocates state, resets the chip, builds platform data from supplied data or defaults plus optional DT properties, clamps initial brightness, writes brightness and configuration registers, sets LED-enable bits, registers a platform backlight, and updates status. Brightness writes split a 12-bit value across LSB/MSB registers. Power state controls standby bit in the command register.

## State and persistence
Runtime state is device-managed. Hardware configuration registers persist until changed or reset. The backlight core stores requested brightness and power state.

## Dependencies and integration points
It depends on I2C SMBus byte operations, optional OF properties (`label`, `default-brightness`, `led-sources`, `arc,*`), and the backlight core.

## Risks and test signals
Risks include unchecked negative SMBus reads when building defaults, no chip-ID verification despite ID registers, DT `led-sources` bit indexing assumptions, ignored return from initial LED enable update, and reset-on-remove side effects. Test signals include DT/default probe paths, invalid LED sources, brightness split at boundaries 0/15/16/4095, power standby toggling, reset failure, and I2C read/write error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/arcxcnn_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/as3711_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/as3711_bl.c

## Purpose
This platform driver exposes AS3711 PMIC step-up converters SU1/SU2 as backlight devices, with emphasis on current-feedback SU2 operation.

## Important APIs, types, and functions
`struct as3711_bl_data` stores per-supply type, brightness, power flag, and backlight pointer. `struct as3711_bl_supply` groups SU1/SU2 state, platform data, and parent AS3711 handle. Key functions are `as3711_set_brightness_auto_i`, `as3711_set_brightness_v`, `as3711_bl_su2_reset`, `as3711_bl_update_status`, `as3711_bl_init_su2`, `as3711_bl_register`, `as3711_backlight_parse_dt`, and probe.

## Control flow
Probe requires platform data, optionally parses a parent OF `backlight` child, validates that at least one framebuffer/supply is selected, then deliberately rejects untested modes except a narrow SU2 auto-current/GPIO4 path. SU2 initialization configures feedback source and current-control bits. Brightness updates write voltage or current registers depending on feedback mode; auto-current first writes quarter current, resets SU2, waits, then writes full current.

## State and persistence
Per-supply brightness is cached for `get_brightness`. Hardware state is in AS3711 regmap registers and persists until reconfigured. Device-managed allocations handle lifetime.

## Dependencies and integration points
It depends on the AS3711 MFD/regmap interface, platform data/OF parsing, and the backlight core.

## Risks and test signals
Risks include intentionally disabled modes, possible hardware damage in untested configurations, complex DT validation, brightness/current scaling assumptions, and SU2 reset timing. Test signals include accepted SU2 auto-current DT, rejected modes, max current clamping, brightness 0/nonzero transition, regmap failure injection, and hardware current measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/as3711_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/aw99706.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/aw99706.c

## Purpose
This I2C/regmap driver controls the Awinic AW99706 WLED backlight controller, including DT-driven initialization of dimming mode, boost frequency/current limit, LED current, UVLO threshold, ramp control, enable GPIO, and 12-bit brightness.

## Important APIs, types, and functions
`struct aw99706_dt_prop` describes property conversion into register fields. `struct aw99706_device` stores client, regmap, backlight, enable GPIO, init table, and enable state. Important functions are DT property lookup/conversion helpers, `aw99706_dt_parse`, `aw99706_hw_init`, `aw99706_bl_enable`, `aw99706_update_brightness`, `aw99706_bl_update_status`, readable/writeable regmap callbacks, `aw99706_chip_id_read`, probe/remove, and PM callbacks.

## Control flow
Probe initializes regmap, reads and validates chip ID, parses DT/default properties into masked register writes, obtains the enable GPIO, powers hardware, writes init fields, registers a raw linear backlight, and stores state. Brightness writes MSB/LSB registers, then toggles the backlight enable bit when zero/nonzero state changes. Remove and suspend drive brightness to zero; remove also drops the hardware enable GPIO after a delay. Resume reruns hardware init.

## State and persistence
Driver state tracks initialization fields and cached enable state. Hardware registers persist while powered; resume reprograms configuration but does not explicitly restore a nonzero brightness.

## Dependencies and integration points
It depends on I2C, regmap-I2C, GPIO descriptors, device properties/OF, bitfield helpers, delays, PM, and the backlight core.

## Risks and test signals
Risks include chip-ID read before asserting enable GPIO if hardware requires it, resume not restoring brightness, property conversion edge cases, protected MTP registers, and max-brightness/default-brightness consistency. Test signals include property default/invalid handling, enable GPIO polarity, chip-ID mismatch, brightness 0/1/4095, suspend/resume brightness restoration expectations, and regmap access-policy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/aw99706.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/backlight.c

## Purpose
`backlight.c` implements the Linux backlight class core. It provides `/sys/class/backlight` devices, common brightness/power attributes, registration helpers, display blanking notifications, PM integration, uevents, and OF lookup helpers.

## Important APIs, types, and functions
Public exports include `backlight_notify_blank`, `backlight_notify_blank_all`, `backlight_device_set_brightness`, `backlight_force_update`, `backlight_device_register`, `backlight_device_unregister`, `devm_backlight_device_register`, `devm_backlight_device_unregister`, `backlight_device_get_by_type`, `backlight_device_get_by_name`, `of_find_backlight_by_node`, and `devm_of_find_backlight`. Attribute handlers implement `bl_power`, `brightness`, `actual_brightness`, `max_brightness`, `scale`, and `type`.

## Control flow
Class initialization runs at `postcore_initcall`. Drivers register a backlight with ops and properties. Sysfs stores validate and update requested brightness/power under `ops_lock`, call driver `update_status`, and emit change events. `actual_brightness` either calls driver `get_brightness` or returns cached brightness. Display blanking adjusts `use_count` and toggles `BL_CORE_FBBLANK`, while suspend/resume toggles `BL_CORE_SUSPENDED` for drivers opting into core PM.

## State and persistence
Each `backlight_device` owns props, ops pointer, update/ops locks, use count, and list entry. A global list protected by `backlight_dev_list_mutex` supports enumeration and blank-all notifications. State is runtime-only but surfaced to userspace through sysfs.

## Dependencies and integration points
It integrates with the Linux device/class model, sysfs, kobject uevents, devres, OF phandles, display drivers, optional PMAC backlight global state, and all low-level backlight drivers.

## Risks and test signals
Risks include stale ops during unregister, global list reference lifetime, `backlight_device_get_by_type` returning without taking a reference, brightness event generation after failed set, blanking use-count correctness, and OF lookup defer behavior. Test signals include sysfs ABI tests, concurrent unregister and sysfs access, blanking multiple displays, suspend/resume, devm cleanup, OF deferred probe, and uevent source checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/bd6107.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/bd6107.c

## Purpose
This I2C driver controls the ROHM BD6107 LED driver as a raw backlight, including reset GPIO handling and optional display-device scoping for blanking notifications.

## Important APIs, types, and functions
`struct bd6107` stores the I2C client, registered backlight, platform data, and reset GPIO. Key routines are `bd6107_write`, `bd6107_backlight_update_status`, `bd6107_backlight_controls_device`, `bd6107_probe`, and `bd6107_remove`.

## Control flow
Probe requires platform data and SMBus byte-data support, requests an active-low reset GPIO initially asserted, registers a raw backlight named after the I2C device, clamps default brightness to max 128, and updates status. Nonzero brightness selects three LED ports, writes the main current value, and enables LED output. Zero brightness asserts reset, waits 24 ms, then deasserts reset. Remove forces brightness zero and updates.

## State and persistence
Runtime state is device-managed except platform data. Hardware state is primarily reset and LED/current registers. The backlight core stores brightness; the driver does not implement readback.

## Dependencies and integration points
It depends on I2C SMBus, GPIO descriptors, legacy platform data, and the backlight core. `controls_device` allows blanking callbacks to affect only the configured display device.

## Risks and test signals
Risks include no DT path in this file, ignored I2C write return values during update, reset polarity assumptions, missing `bd->backlight` assignment despite struct field, and all brightness-off operations resetting the chip. Test signals include platform-data absence, reset GPIO polarity, brightness 0/nonzero/max, display-specific blanking, I2C write failure visibility, and remove path reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/bd6107.c -->
