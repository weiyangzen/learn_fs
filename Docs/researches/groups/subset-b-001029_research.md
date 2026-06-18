# subset-b-001029 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/video_detect.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/video_detect.c

### Purpose
`video_detect.c` centralizes ACPI backlight-provider selection. It decides whether the system should expose ACPI video backlight control, native GPU backlight control, vendor/platform control, NVIDIA WMI EC control, Apple gmux, Dell UART, or no backlight device.

### Important APIs, Types, And Functions
The exported API is `__acpi_video_get_backlight_type(bool native, bool *auto_detect)`. Internal helpers parse `acpi_video_backlight_string`, walk ACPI namespace devices via `find_video()`, probe NVIDIA WMI EC support with `nvidia_wmi_ec_supported()`, detect Google EC, Apple gmux, and Dell UART backlight devices, and apply DMI callbacks such as `video_detect_force_vendor()`, `video_detect_force_video()`, `video_detect_force_native()`, and `video_detect_portege_r100()`. The large `video_detect_dmi_table` is the main policy database.

### Control Flow
The first call takes `init_mutex`, parses command-line policy, applies DMI quirks, walks ACPI devices for `ACPI_VIDEO_HID` devices backed by PCI graphics devices, and caches special-controller presence. Later calls only update `native_available` when GPU drivers report native backlight availability. Decision precedence is command line, DMI quirk, special controllers, ACPI video unless native is preferred on Win8+/Chromebook systems, native, `none` for Win8+ systems with no provider yet, then vendor for old hardware.

### State, Persistence, And Dependencies
State is process-wide static cache: command-line choice, DMI result, feature-detection booleans, `native_available`, `video_caps`, and `init_done`. It depends on ACPI namespace walking, DMI, PCI lookup, WMI, `apple_gmux_detect()`, Dell ACPI HIDs, OSI Win8 detection, and GPU drivers calling the native query path.

### Integration Points
Backlight drivers use this to avoid registering competing `/sys/class/backlight` devices. It integrates with `video.ko`, GPU DRM drivers, vendor laptop drivers, `nvidia-wmi-ec-backlight`, `apple-gmux`, Dell UART backlight, Chromebook EC handling, and boot parameter parsing.

### Risks
The risk is mostly policy misclassification: a wrong DMI entry can suppress the only working backlight path, create duplicate controls, or select a provider whose key events/userspace expectations differ. The `native_available` cache makes call order observable, so GPU probe timing affects fallback behavior. The namespace walk intentionally only treats ACPI video devices with PCI graphics backing as usable, which can miss unusual firmware.

### Test Signals
Useful signals are exact backlight provider selected under command-line overrides, DMI quirk coverage on listed systems, absence of duplicate backlight devices, brightness key behavior before and after GPU driver load, Win8+/Chromebook defaulting to native, and NVIDIA EC/Apple gmux/Dell UART detection on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/video_detect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/viot.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/viot.c

### Purpose
`viot.c` implements support for the ACPI Virtual I/O Translation Table. It maps PCI and MMIO endpoints to para-virtual virtio-iommu nodes so DMA configuration can attach endpoints to the correct IOMMU before device drivers probe.

### Important APIs, Types, And Functions
Key types are `struct viot_iommu` and `struct viot_endpoint`. Initialization APIs are `acpi_viot_early_init()` and `acpi_viot_init()`. Runtime configuration enters through `viot_iommu_configure(struct device *dev)`, which dispatches to PCI alias handling or MMIO platform-device matching. Helpers include `viot_check_bounds()`, `viot_get_iommu()`, `viot_parse_node()`, and `viot_dev_iommu_init()`.

### Control Flow
Early init checks for a VIOT table and requests PCI ACS before bus scan. Main init fetches the table, iterates `node_count` nodes from `node_offset`, validates bounds and length, interns virtio-iommu nodes, and records endpoint ranges. During `dma_configure()`, PCI devices iterate DMA aliases against VIOT PCI ranges and calculate endpoint IDs from segment/BDF offsets; platform devices match their first MMIO resource base. Successful matches call `acpi_iommu_fwspec_init()`.

### State, Persistence, And Dependencies
Global state includes the ACPI table pointer and three lists: IOMMU nodes, PCI ranges, and MMIO endpoints. The table memory is obtained from ACPI; endpoint/IOMMU records are heap allocated and retained for the life of the boot. Dependencies include ACPI VIOT structs, PCI lookup, ACPI resource consumers, fwnode allocation, virtio-iommu configuration, and the IOMMU core.

### Integration Points
The file plugs into ACPI table initialization and generic DMA setup. It bridges firmware topology to `iommu_fwspec`, supports PCI aliases, and uses device fwnodes to identify virtio-iommu providers even when PCI IOMMU devices lack ACPI nodes.

### Risks
Malformed table bounds, short node lengths, stale output-node offsets, missing provider devices, or incorrect endpoint ID arithmetic can prevent endpoint probing or attach devices to the wrong IOMMU. `acpi_viot_init()` returns early on parse errors without freeing prior allocations, acceptable during init but important for fault interpretation.

### Test Signals
Test by booting with valid/invalid VIOT tables, confirming ACS request before PCI scan, verifying probe deferral until virtio-iommu exists, checking PCI alias endpoint IDs, MMIO resource matching, and DMA mappings flowing through virtio-iommu ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/viot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/wakeup.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/wakeup.c

### Purpose
`wakeup.c` manages ACPI wakeup devices around system sleep and provides a small callback registry for drivers whose wake IRQ is shared with the ACPI SCI.

### Important APIs, Types, And Functions
The main APIs are `acpi_enable_wakeup_devices()`, `acpi_disable_wakeup_devices()`, `acpi_wakeup_device_init()`, `acpi_register_wakeup_handler()`, `acpi_unregister_wakeup_handler()`, and `acpi_check_wakeup_handlers()`. `struct acpi_wakeup_handler` stores a callback and opaque context on a protected list.

### Control Flow
Enable/disable paths iterate `acpi_wakeup_device_list`, skip invalid or unsupported sleep states, require either `device_may_wakeup()` or ACPI prepare count, then set GPE wake masks and optionally power wake devices. Init enables button GPEs and turns on wakeup for devices capable of wake. SCI-shared handlers are only registered when the given IRQ equals `acpi_sci_irq`; wake checking calls handlers until one reports true.

### State, Persistence, And Dependencies
State lives in ACPI device wake flags, GPE masks, wake power state, and the static handler list guarded by `acpi_wakeup_handler_mutex`. Sleep entry/exit code calls this while hotplug is effectively quiesced, so the device list is not locked in the suspend paths.

### Integration Points
This code integrates ACPI core wake device discovery, device power-management wake flags, GPE programming, ACPI sleep transitions, and drivers that need to distinguish SCI wake from a shared device interrupt.

### Risks
Incorrect wake mask handling can either miss wake events or leave spurious wake sources armed. Handler unregister walks with `list_for_each_entry()` and deletes a matching entry then breaks; callers must avoid duplicate registrations with the same callback/context. `acpi_check_wakeup_handlers()` intentionally runs without locking, so it relies on sleep serialization.

### Test Signals
Signals include wake from buttons and device GPEs in supported S-states, wake power enable/disable pairing, SCI-shared IRQ devices reporting wake correctly, no wake handler leaks after driver unload, and no spurious wake storms after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/Makefile -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/Makefile

### Purpose
This Makefile selects the x86-specific ACPI support objects that are linked into the ACPI x86 helper object or built independently for x86 blacklist handling.

### Important APIs, Types, And Functions
There are no runtime APIs. Build variables add `apple.o`, `cmos_rtc.o`, `s2idle.o`, and `utils.o` to `acpi-x86.o`, add `lpss.o` only with `CONFIG_PCI`, and build `blacklist.o` when `CONFIG_X86` is enabled.

### Control Flow
Build-time control flow is Kbuild conditional expansion. `obj-$(CONFIG_ACPI)` emits `acpi-x86.o`; `acpi-x86-$(CONFIG_PCI)` gates LPSS support because it depends on PCI helpers and device-link cases.

### State, Persistence, And Dependencies
No runtime state exists. The file encodes compile-time dependencies between x86 ACPI helpers and kernel configuration symbols.

### Integration Points
It feeds the ACPI driver subtree build and determines whether Apple property extraction, CMOS RTC address-space handling, LPSS, s2idle LPS0, and x86 utility quirks are available to ACPI core code.

### Risks
Incorrect gating can cause unresolved symbols or silently omit platform quirks. `blacklist.o` is linked outside `acpi-x86.o`, so changes to ACPI-vs-X86 conditions can affect early blacklist behavior.

### Test Signals
Build matrix coverage with `CONFIG_ACPI`, `CONFIG_X86`, `CONFIG_PCI`, and `CONFIG_X86_INTEL_LPSS` combinations should verify objects are present only when expected and no symbols are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/apple.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/apple.c

### Purpose
`apple.c` converts Apple's custom ACPI `_DSM` property package format into Linux's standard `_DSD`-style software node property representation for Apple x86 machines.

### Important APIs, Types, And Functions
The exported function is `acpi_extract_apple_properties(struct acpi_device *adev)`. It uses the Apple property GUID, `acpi_evaluate_dsm_typed()`, bitmaps to track valid key/value pairs, ACPI object allocation, and `acpi_data_add_props()`.

### Control Flow
The function returns unless `x86_apple_machine` is true. It evaluates `_DSM` function 0 as a buffer, requires version byte 3, then evaluates function 1 as a package. The package is parsed as alternating key/value objects, accepting string keys and integer, buffer, or string values. Valid properties are copied into a newly allocated top-level package of two-element key/value packages and attached to `adev->data`.

### State, Persistence, And Dependencies
Converted properties are stored in `adev->data.pointer` and added under the Apple GUID, persisting with the ACPI device. Temporary ACPI objects and bitmaps are freed. Dependencies include Apple-specific firmware contracts, ACPI object layout, bitmap helpers, and the ACPI device property subsystem.

### Integration Points
This runs during ACPI device setup for Apple hardware so normal Linux drivers can consume firmware properties without understanding Apple's nonstandard `_DSM` encoding.

### Risks
The function trusts package count pairing and sizes its output buffer manually. Incorrect size accounting or invalid firmware object types could drop properties; the final `WARN_ON()` catches layout drift. It only supports protocol version 3.

### Test Signals
Test on Apple hardware with known `_DSM` properties, verify invalid properties are skipped with diagnostics, properties are visible through fwnode/property APIs, and no leaks occur when version or allocation checks fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/blacklist.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/blacklist.c

### Purpose
`blacklist.c` handles early x86 ACPI firmware blacklisting and optional DMI-based `_REV` override quirks for machines whose firmware behavior depends on Windows-like ACPI revision reporting.

### Important APIs, Types, And Functions
The main API is `acpi_blacklisted()`. It uses `acpi_match_platform_list()` against `acpi_blacklist`, calls `early_acpi_osi_init()`, and optionally scans `acpi_rev_dmi_table`. With `CONFIG_ACPI_REV_OVERRIDE_POSSIBLE`, `dmi_enable_rev_override()` calls `acpi_rev_override_setup(NULL)`.

### Control Flow
During early ACPI setup, the code matches OEM table IDs/revisions against known broken DSDTs. A match logs vendor, table, reason, and recoverability and returns the critical flag. It then initializes early OSI handling and applies DMI `_REV` overrides for selected Dell systems.

### State, Persistence, And Dependencies
The blacklist table is `__initdata`; DMI revision table is `__initconst`. Persistent effects are the return value controlling ACPI continuation and global `_REV` override state set by `acpi_rev_override_setup()`.

### Integration Points
This is part of early ACPI boot policy. It coordinates with ACPI table matching, DMI, OSI initialization, audio/ethernet quirks on Dell systems, and kernel config options controlling whether `_REV` override is possible.

### Risks
False positives can disable ACPI or alter firmware paths unnecessarily; false negatives can boot with known nonrecoverable firmware defects. DMI `_REV` override is machine-specific because it can change device exposure and method behavior.

### Test Signals
Boot logs should show blacklist and `_REV` notices only on matching hardware. ACPI disabled/continued behavior should match critical flags, and Dell listed systems should expose expected audio/network devices under the override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/blacklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/cmos_rtc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/cmos_rtc.c

### Purpose
`cmos_rtc.c` installs an ACPI CMOS address-space handler and creates platform devices for ACPI RTC/TAD devices so AML can access CMOS RTC fields through `ACPI_ADR_SPACE_CMOS`.

### Important APIs, Types, And Functions
The entry point is `acpi_cmos_rtc_init()`, registering `cmos_rtc_handler`. The attach path calls `acpi_install_cmos_rtc_space_handler()` and `acpi_create_platform_device()`. `acpi_cmos_rtc_space_handler()` performs byte reads/writes through `CMOS_READ()` and `CMOS_WRITE()`.

### Control Flow
Matching HIDs include `ACPI000E` and standard CMOS RTC IDs. The first attached device installs the address-space handler once. Each attach attempts platform-device creation; for non-TAD RTC IDs it sets `cmos_rtc_platform_device_present` when the platform device was created.

### State, Persistence, And Dependencies
State includes the global `cmos_rtc_platform_device_present` flag and the static once-only handler-installed flag. CMOS hardware state persists outside the driver. Access is serialized by `rtc_lock` with IRQ-safe spin locking.

### Integration Points
This bridges ACPI AML operation regions to the mc146818 RTC implementation and ACPI scan platform-device creation. Other x86 ACPI code can check whether a CMOS RTC platform device exists.

### Risks
The handler rejects base addresses above 0xff but does not explicitly reject multi-byte accesses that cross 0xff after the first byte. Incorrect AML writes can modify persistent RTC/CMOS registers. Handler installation failure logs but blocks attach with `-ENODEV`.

### Test Signals
Signals include successful ACPI scan attachment for RTC/TAD devices, AML CMOS region reads/writes matching hardware registers, platform device creation, correct locking under concurrent RTC access, and graceful behavior if the handler is already installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/cmos_rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/lpss.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/lpss.c

### Purpose
`lpss.c` enumerates and manages Intel Low Power Subsystem ACPI devices on x86. It creates platform devices, registers per-device clocks, applies PWM/UART/I2C/SPI quirks, exposes LTR diagnostics, and provides a custom PM domain for LPSS context save/restore and power sequencing.

### Important APIs, Types, And Functions
Core types are `struct lpss_device_desc`, `struct lpss_private_data`, and `struct lpss_device_links`. Entry point `acpi_lpss_init()` registers an ACPI scan handler and platform bus notifier. Key helpers are `acpi_lpss_create_device()`, `register_device_clock()`, `acpi_lpss_save_ctx()`, `acpi_lpss_restore_ctx()`, `acpi_lpss_suspend()`, `acpi_lpss_resume()`, `acpi_lpss_set_ltr()`, and IOSF D3 helpers for Atom LPSS DMA power quirks.

### Control Flow
ACPI IDs map to descriptors for Lynxpoint, BayTrail, Braswell, Broadwell, DMA, PWM, UART, I2C, SPI, and SDIO devices. Attach maps the first memory resource, runs descriptor setup, registers clocks if required, fixes up ACPI power state, creates a platform device, and creates selected device links from `_DEP`/DMI data. Platform bus notifications install/remove the LPSS PM domain and LTR sysfs group. PM callbacks save private registers, call ACPI power transitions, add D3-to-D0 delay where needed, restore context, and handle late/noirq sequencing for devices that must resume early.

### State, Persistence, And Dependencies
Each ACPI device stores `lpss_private_data` in `adev->driver_data`, including MMIO mapping, clock pointer, fixed clock rate, descriptor, and saved private-register context. Global state includes the LPSS clock platform device, Atom D3 mask, LPSS quirks, IOSF mutex, and D3-entered flag. Dependencies span ACPI scan/power, PCI, platform devices, clk framework, PWM lookup tables, runtime PM, DMI, IOSF MBI, PMC Atom registers, and property entries for child drivers.

### Integration Points
It is the platform glue for downstream drivers such as DesignWare UART/I2C, PXA2xx SPI, PWM LPSS, SDIO, and LPSS DMA. Device links keep GPU/SD card dependencies ordered against PMIC I2C controllers. LTR sysfs and `set_latency_tolerance` integrate with PM QoS-style latency tolerance.

### Risks
LPSS devices can hang the system if accessed while unpowered, so PM ordering and the always-power-on DMA quirk are critical. MMIO size checks protect LTR access, but descriptor offsets must match hardware. Context save after firmware has powered off a block can save `0xffffffff`, hence `SAVE_CTX_ONCE`. Device-link DMI exceptions can alter suspend behavior on specific tablets.

### Test Signals
Test enumeration on Lynxpoint/BayTrail/Braswell/Broadwell systems, per-device clock registration and rates, UART RTS override behavior, I2C reset and shared-host handling, PWM lookup consumers, LTR sysfs reads, runtime suspend/resume, S0ix suspend cycles, context retention, and absence of DMA island hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/lpss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/s2idle.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/s2idle.c

### Purpose
`s2idle.c` provides x86 ACPI Low Power S0 Idle support. It discovers the LPS0 device, validates platform `_DSM` interfaces, sequences entry/exit notifications around suspend-to-idle, optionally checks device constraints, and lets other drivers register LPS0 callbacks.

### Important APIs, Types, And Functions
The setup API is `acpi_s2idle_setup()`. Exported registration APIs are `acpi_register_lps0_dev()` and `acpi_unregister_lps0_dev()`. Internal helpers include `validate_dsm()`, `lps0_device_attach()`, `lpi_device_get_constraints()`, `lpi_device_get_constraints_amd()`, `lpi_check_constraints()`, and the platform s2idle ops wrappers.

### Control Flow
ACPI scan attaches to `PNP0D80`, validates Microsoft, AMD, or generic LPS0 DSM UUIDs, handles AMD function-mask quirks, sets suspend-to-idle as default when FADT Low Power S0 is set and S3 was not chosen, and marks EC GPE wake-capable. At suspend begin, constraints are fetched once if requested. Late prepare checks constraints, sends screen-off and LPS0/Modern Standby entry DSM calls, then invokes registered prepare callbacks. Restore invokes registered callbacks, then sends exit, display-on intent, Modern Standby exit, and screen-on DSM calls.

### State, Persistence, And Dependencies
Global state records the LPS0 handle, DSM GUIDs and masks, current DSM state, revision ID, constraint table, and registered device ops list. Module parameters `sleep_no_lps0` and `check_lps0_constraints` persist as runtime policy. Dependencies include ACPI DSM evaluation, suspend core `platform_s2idle_ops`, FADT flags, CPU vendor detection, EC wake handling, system sleep locking, and ACPI power-state data.

### Integration Points
This file links ACPI firmware LPS0 contracts with Linux suspend-to-idle. Drivers needing platform-specific hooks can register `acpi_s2idle_dev_ops`, and ACPI core sleep ops provide begin/prepare/check/wake/restore/end plumbing.

### Risks
DSM function ordering is firmware-sensitive and differs between AMD, Microsoft, and generic UUIDs. AMD Picasso-style off-by-one masks are corrected heuristically. Constraint parsing trusts nested package shapes enough to inspect them, so malformed firmware can disable useful diagnostics. Registered callback lists are protected by system sleep locks, not general-purpose list locks.

### Test Signals
Signals include LPS0 selected by default only when expected, DSM function masks logged correctly, suspend/resume DSM call order on AMD and non-AMD platforms, constraint warnings when devices stay above required D-states, EC wake behavior, and registered device callbacks running in prepare/check/restore phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/s2idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/utils.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/x86/utils.c

### Purpose
`utils.c` collects x86 ACPI platform quirks: overriding broken `_STA` results, forcing NVMe Storage D3 policy on modern AMD systems, skipping bogus Android-tablet I2C/serdev/AC/battery/GPIO enumeration, creating Dell UART backlight glue, and disabling mwait on a known-bad system.

### Important APIs, Types, And Functions
Exported or externally used APIs include `acpi_device_override_status()`, `force_storage_d3()`, `acpi_quirk_skip_i2c_client_enumeration()`, `acpi_quirk_skip_serdev_enumeration()`, `acpi_quirk_skip_gpio_event_handlers()`, `acpi_quirk_skip_acpi_ac_and_battery()`, and `acpi_proc_quirk_mwait_check()`. Key data structures are `override_status_id` and DMI quirk tables.

### Control Flow
Status override checks CPU model, optional DMI, then HID/UID or full ACPI path and returns a replacement status. Storage D3 returns true for Zen systems with FADT Low Power S0. Android-tablet helpers match DMI quirk bitmasks, skip unsafe I2C clients except known-good PMIC/audio/keyboard HIDs, skip or redirect serdev enumeration based on UART UID, skip GPIO event handlers, and suppress ACPI AC/battery when native PMIC drivers are preferable. Dell `DELL0501` causes a `dell-uart-backlight` platform device and skips serdev child enumeration.

### State, Persistence, And Dependencies
The file is mostly stateless policy, but it creates a static platform device for Dell UART backlight and can set global `boot_option_idle_override = IDLE_NOMWAIT`. It depends on DMI, ACPI device matching, CPU model matching, PCI devfn fallback for UART UID, platform-device registration, and optional `CONFIG_X86_ANDROID_TABLETS`.

### Integration Points
ACPI scan uses `_STA` override; I2C, serdev, GPIO, battery/AC, storage, and processor idle paths consume the quirk APIs. It coordinates with `drivers/platform/x86/x86-android-tablets.c` for manual device instantiation on broken Android x86 tablets.

### Risks
Quirks can hide real devices or expose bogus devices, causing resource conflicts, missing input sensors, broken charging, or wrong UART client creation. DMI strings are sometimes generic, so entries add BIOS dates or exact matches. The Storage D3 broad AMD policy intentionally compensates for missing firmware properties but may affect NVMe power behavior.

### Test Signals
Test exact DMI systems for intended device visibility, I2C known-good exceptions, serdev skip/tty fallback behavior, Dell UART backlight platform creation, PMIC AC/battery suppression, NVMe D3 during s2idle on AMD, and mwait disabled on the Acer Extensa quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/x86/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/amba/Kconfig

### Purpose
This Kconfig file defines the AMBA bus enable symbol and the optional Tegra AHB configuration driver.

### Important APIs, Types, And Functions
There are no runtime APIs. `ARM_AMBA` is a boolean umbrella symbol. `TEGRA_AHB` is a boolean option visible under `COMPILE_TEST`, defaulting to yes on `ARCH_TEGRA`, with help text describing AHB arbitration and performance tuning.

### Control Flow
Configuration flow gates the Tegra AHB option inside `if ARM_AMBA`. Build inclusion then follows the Makefile's `obj-$(CONFIG_...)` rules.

### State, Persistence, And Dependencies
No runtime state exists. The file persists platform support decisions in kernel configuration. `TEGRA_AHB` depends implicitly on `ARM_AMBA` through menu nesting.

### Integration Points
It controls whether `bus.c` and `tegra-ahb.c` are buildable and exposes Tegra AHB support for Tegra platforms or compile-test builds.

### Risks
Misconfiguration can omit the AMBA bus or Tegra AHB performance setup. Because `TEGRA_AHB` defaults on for Tegra, changing defaults affects platform boot/performance assumptions.

### Test Signals
Kconfig tests should cover `ARCH_TEGRA`, `COMPILE_TEST`, and non-AMBA builds, confirming expected symbols and object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/Makefile -->
## sources/distributed-fs/ceph-client/drivers/amba/Makefile

### Purpose
This Makefile maps AMBA-related configuration symbols to object files.

### Important APIs, Types, And Functions
There are no runtime APIs. `CONFIG_ARM_AMBA` builds `bus.o`; `CONFIG_TEGRA_AHB` builds `tegra-ahb.o`.

### Control Flow
Kbuild expands object lists according to configuration. `bus.o` provides the core AMBA bus type and exported helpers; `tegra-ahb.o` provides NVIDIA Tegra AHB register programming.

### State, Persistence, And Dependencies
No runtime state exists. The Makefile depends on Kconfig symbols from the same directory and architecture/platform selections.

### Integration Points
It connects AMBA core support and Tegra-specific AHB support into the kernel driver build.

### Risks
Wrong object mapping causes missing bus registration or missing Tegra AHB init. Since AMBA drivers depend on `amba_bustype`, omitting `bus.o` breaks all AMBA device binding.

### Test Signals
Build tests should verify object inclusion for `CONFIG_ARM_AMBA=y` and `CONFIG_TEGRA_AHB=y`, plus absence when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/bus.c -->
## sources/distributed-fs/ceph-client/drivers/amba/bus.c

### Purpose
`bus.c` implements the Linux AMBA bus for ARM PrimeCell/CoreSight-style devices: matching, probing, PM, DMA setup, device allocation/registration, driver registration, sysfs attributes, and memory-region helpers.

### Important APIs, Types, And Functions
Exported APIs include `amba_bustype`, `dev_is_amba()`, `__amba_driver_register()`, `amba_driver_unregister()`, `amba_device_add()`, `amba_device_alloc()`, `amba_device_register()`, `amba_device_put()`, `amba_device_unregister()`, `amba_request_regions()`, and `amba_release_regions()`. Internal flow uses `amba_lookup()`, `amba_read_periphid()`, `amba_match()`, `amba_probe()`, `amba_remove()`, and runtime PM callbacks.

### Control Flow
Device registration claims the parent memory resource and tries to read peripheral/component IDs; if resources are not ready, uevents are suppressed until match can power the device, enable `apb_pclk`, deassert reset, ioremap, read PID/CID registers, and resubmit an add uevent. Matching honors `driver_override` before ID table lookup. Probe decodes OF IRQs, applies OF clock defaults, attaches PM domain, enables pclk, enables runtime PM, and calls the AMBA driver's probe. Remove reverses runtime PM and clock setup.

### State, Persistence, And Dependencies
Each `amba_device` carries peripheral ID, component ID, CoreSight UCI data, pclk, resource, IRQs, DMA masks/params, override string, and `periphid_lock`. The bus depends on clocks, resets, OF, ACPI DMA configuration, IOMMU default domains, PM domains, runtime PM, and Linux device core.

### Integration Points
It is the binding layer for AMBA drivers and supports both OF and ACPI firmware paths. It emits `AMBA_ID` and modalias uevents for module loading and registers a late stub driver when modules are enabled so ID reads can occur even before real AMBA drivers load.

### Risks
ID reads require powered and clocked hardware; failures are mapped to `-EPROBE_DEFER` in match to avoid driver registration failure. Clock/PM-domain cleanup is subtle on probe failure paths. DMA cleanup assumes a valid driver object and respects `driver_managed_dma`. Runtime PM clock toggling must honor IRQ-safe devices.

### Test Signals
Signals include correct sysfs `id`, `resource`, and `driver_override`; module autoload modaliases; deferred ID read recovery; CoreSight UCI matching; probe/remove clock balance; OF IRQ decoding; ACPI/OF DMA setup; IOMMU default-domain use; and region request/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/tegra-ahb.c -->
## sources/distributed-fs/ceph-client/drivers/amba/tegra-ahb.c

### Purpose
`tegra-ahb.c` programs NVIDIA Tegra AHB arbitration, gizmo, and prefetch registers for performance and SMMU coordination, and saves/restores those registers across suspend.

### Important APIs, Types, And Functions
The platform driver is `tegra_ahb_driver`. Key helpers are `tegra_ahb_gizmo_init()`, `tegra_ahb_probe()`, suspend/resume callbacks, `gizmo_readl()`, `gizmo_writel()`, and, with `CONFIG_TEGRA_IOMMU_SMMU`, exported `tegra_ahb_enable_smmu(struct device_node *dn)`.

### Control Flow
Probe allocates `struct tegra_ahb` with a flexible context array, fetches MMIO resource 0, corrects legacy DT base addresses ending in low byte `0x4`, maps registers, stores drvdata, and initializes arbitration/prefetch state. Suspend copies all listed AHB gizmo registers into `ctx`; resume writes them back. SMMU enable finds the AHB device by OF node and sets `SMMU_INIT_DONE`.

### State, Persistence, And Dependencies
State includes MMIO base, device pointer, and saved register context. Hardware register state controls arbitration priorities, USB/AHBDMA prefetch, immediate modes, write splitting, and SMMU init indication. Dependencies include platform driver core, OF matching, devm resource mapping, PM ops, and optional Tegra SMMU integration.

### Integration Points
The driver binds to `nvidia,tegra30-ahb` and `nvidia,tegra20-ahb`. It coordinates with Tegra USB/AHBDMA traffic behavior and the Tegra SMMU driver through the exported init-done API.

### Risks
The base-address workaround mutates the resource start in place for legacy DTs, which is intentional but broad for affected resources. Incorrect register programming can degrade bus fairness or USB/DMA throughput. Suspend context must cover every register modified by init or platform firmware.

### Test Signals
Test probe on legacy and corrected DT bases, readback of priority/prefetch bits, USB/DMA throughput, SMMU init-done handoff, suspend/resume register restoration, and module alias/platform binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/amba/tegra-ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/android/Kconfig

### Purpose
This Kconfig menu exposes Android Binder IPC, the Rust Binder implementation, BinderFS, binder device naming, and Binder allocator KUnit tests.

### Important APIs, Types, And Functions
There are no runtime functions in this file. Symbols are `ANDROID_BINDER_IPC`, `ANDROID_BINDER_IPC_RUST`, `ANDROID_BINDERFS`, `ANDROID_BINDER_DEVICES`, and `ANDROID_BINDER_ALLOC_KUNIT_TEST`.

### Control Flow
Configuration dependencies ensure C Binder requires `MMU` and `NET`, Rust Binder requires `RUST`, `MMU`, and not C Binder, BinderFS depends on C Binder, device-name string is available for either Binder implementation, and allocator KUnit tests depend on C Binder plus KUnit.

### State, Persistence, And Dependencies
Kernel configuration persists chosen Binder implementation and default device names. The default Binder devices string is `binder,hwbinder,vndbinder`.

### Integration Points
The menu controls build inclusion for Android IPC drivers and testing support. BinderFS enables per-IPC-namespace Binder device allocation through a pseudo filesystem, while `ANDROID_BINDER_DEVICES` feeds binder device creation parameters.

### Risks
Selecting Rust Binder excludes C Binder, and BinderFS currently depends only on the C implementation. Misconfigured device names can break Android userspace expectations. KUnit test selection pulls test code into builds when enabled.

### Test Signals
Kconfig/build tests should cover C Binder, Rust Binder, BinderFS dependency behavior, custom `ANDROID_BINDER_DEVICES`, and KUnit test module inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/Makefile -->
## sources/distributed-fs/ceph-client/drivers/android/Makefile

### Purpose
This Makefile maps Android driver configuration symbols to Binder, BinderFS, Binder allocator test, and Rust Binder build targets.

### Important APIs, Types, And Functions
There are no runtime APIs here. It adds `-I$(src)` to `ccflags-y` for trace event includes. Objects are `binderfs.o`, `binder.o`, `binder_alloc.o`, `binder_netlink.o`, `tests/`, and `binder/` for the Rust implementation.

### Control Flow
Kbuild conditionals include BinderFS, C Binder components, allocator KUnit tests, and Rust Binder according to Kconfig symbols.

### State, Persistence, And Dependencies
No runtime state exists. The compile flag is a build-time dependency for local trace headers. Object selection depends on Android Kconfig choices.

### Integration Points
It connects Android IPC sources to the kernel build and separates C Binder from Rust Binder directory builds while sharing the surrounding Android driver menu.

### Risks
Removing the local include flag can break trace-event compilation. Object mapping must remain synchronized with Kconfig dependencies, especially BinderFS and tests depending on C Binder.

### Test Signals
Build tests should verify all Android configuration combinations, trace include resolution, test directory inclusion, and Rust Binder directory build when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/android/Makefile -->
