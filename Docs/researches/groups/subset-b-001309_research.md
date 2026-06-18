# subset-b-001309 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.c

## Purpose
`gpiolib.c` is the core Linux GPIO descriptor framework. It registers GPIO chips as `gpio_device` instances, assigns legacy integer ranges, exposes character/sysfs/debugfs views, implements consumer descriptor lookup and request/free paths, dispatches line direction/value/config operations to chip callbacks, wires GPIO-backed IRQ domains, handles firmware-backed hogs and line names, and maintains hot-unplug-safe chip access.

## Important APIs, types, and functions
Major exported APIs include chip lifecycle (`gpiochip_add_data_with_key()`, `gpiochip_remove()`), descriptor conversion and metadata (`gpio_to_desc()`, `desc_to_gpio()`, `gpiod_hwgpio()`, `gpiod_to_gpio_device()`, `gpio_device_find*()`), consumer acquisition (`gpiod_get*()`, `fwnode_gpiod_get_index()`, `gpiod_get_array*()`, `gpiod_put*()`), line operations (`gpiod_direction_input()`, `gpiod_direction_output*()`, `gpiod_get/set_*value*()`, array get/set variants), configuration (`gpiod_set_config()`, `gpiod_set_debounce()`, `gpiod_set_transitory()`), pinctrl helpers, and IRQ helpers (`gpiod_to_irq()`, `gpiochip_lock_as_irq()`, `gpiochip_irqchip_add_domain()`). Internal state is driven by `struct gpio_device`, `struct gpio_desc`, GPIO descriptor flag bits, the global `gpio_devices` SRCU list, lookup tables, and optional `struct gpio_irq_chip` data.

## Control flow
Chip registration allocates a `gpio_device`, initializes SRCU domains, chooses a firmware node, derives `ngpio`, assigns a dynamic or legacy base, links the device in sorted global range order, sets names and valid masks, imports OF/ACPI pin ranges, applies firmware hogs, initializes IRQ masks/hardware/domains, sets up shared-line support, and registers the cdev/sysfs device if gpiolib core init has completed. Removal reverses that path: sysfs and hogs are removed, remaining line IRQ users are freed, the device is unlinked, `gdev->chip` is nulled under SRCU, shared/IRQ/ACPI/OF/pinctrl state is torn down, and the cdev/device reference is dropped.

Consumer lookup first tries firmware sources in OF, ACPI, or software nodes, including secondary fwnodes, then falls back to platform lookup tables when allowed. The found descriptor is requested with module/device references, configured with lookup and consumer flags, then line-state notifiers are emitted. Direction/value operations validate descriptors, take the GPIO-device SRCU lock, call chip callbacks, normalize positive callback returns to `-EBADE`, update descriptor flags, trace values/directions, and notify user-visible state changes. Array operations group same-chip contiguous descriptors into bitmap fast paths where possible, with fallbacks for mixed chips or open-drain/open-source lines. IRQ setup builds simple or hierarchical irqdomains and wraps mutable irqchip hooks so GPIO line flags track IRQ enable/disable state.

## State and persistence behavior
All state is runtime kernel state. `gpio_devices` and `gpio_lookup_list` are global in-memory registries protected by mutexes and SRCU. Each `gpio_device` owns descriptors, valid masks, pin ranges, notifier chains, cdev/sysfs identity, owner references, and the RCU-protected pointer to the provider `gpio_chip`. Each `gpio_desc` stores request/output/active-low/open-drain/open-source/IRQ/hog/pull/transitory/shared flags, a SRCU-freed label, optional firmware hog node, and optional debounce state. No on-disk persistence exists; firmware properties, static lookup tables, and probe order reconstruct state on boot.

## Dependencies and integration points
The file integrates with the Linux driver core, character devices, sysfs, debugfs, OF/ACPI/software-node GPIO lookup helpers, pinctrl, IRQ domains, irqchip APIs, HTE timestamp hooks, tracepoints, shared GPIO proxy support, and the GPIO uAPI implementation in `gpiolib-cdev`. It is the central boundary between GPIO provider drivers implementing `struct gpio_chip` callbacks and consumers using descriptor APIs.

## Risks and edge cases
The highest-risk areas are hot-unplug and SRCU lifetime rules, legacy integer base overlap, callback error normalization, direction/value calls on unrequested or sleepable chips from atomic context, open-drain/open-source emulation through input mode, IRQ lines being driven as outputs, IRQ domain initialization races returning `-EPROBE_DEFER`, shared GPIO proxy fallback, cleanup of remaining IRQ actions on chip removal, and partial registration unwind. Firmware naming and reserved-range parsing can silently leave lines unnamed or invalid. Array fast paths depend on descriptor layout and hardware offsets matching.

## Test signals
Useful tests include gpiochip probe/remove with dynamic and static bases, OF/ACPI/software-node lookup and hogs, deferred probe when chips are absent, descriptor request/free reference accounting, cdev/sysfs/debugfs visibility, active-low and open-drain/source get/set behavior, sleeping versus atomic access warnings, array fast-path and mixed-chip fallbacks, pinctrl range setup/removal, IRQ domain mapping for simple and hierarchical chips, removal with active IRQ users, and fault injection for allocation and callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.h -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.h

## Purpose
`gpiolib.h` is the private GPIO core header shared by gpiolib implementation files. It defines internal state containers, descriptor flags, helper iteration macros, lookup suffix handling, guard-based SRCU access to chips, logging helpers, and cross-file prototypes for descriptor request/configuration, array I/O, hogging, and line notifications.

## Important APIs, types, and functions
The key types are `struct gpio_device`, `struct gpio_desc`, `struct gpio_array`, `struct gpio_desc_label`, and `struct gpio_chip_guard`. `gpio_device` wraps the driver-core device/cdev, chip pointer, descriptor array, validity masks, SRCU domains, pin ranges, notifier chains, line workqueue, and legacy base. `gpio_desc` carries per-line flags such as requested, output, active-low, open-drain/source, IRQ, hog, pull bias, event clock, and shared-proxy state. Prototypes cover `gpiod_request*()`, `gpiod_free*()`, `gpiod_find_and_request()`, `gpiod_configure_flags()`, `gpiochip_add_hog()`, `gpiochip_get_ngpios()`, and array get/set complex helpers.

## Control flow
The header has no standalone execution, but it shapes core control flow. `DEFINE_CLASS(gpio_chip_guard, ...)` opens the descriptor's GPIO-device SRCU read side and safely dereferences `gdev->chip`, allowing call sites in `gpiolib.c` to abort when a hot-unplugged chip has vanished. `for_each_gpio_property_name()` generates `con_id-gpios`/`con_id-gpio` firmware property names. Descriptor iteration macros let chip registration, debugfs, hog cleanup, and IRQ cleanup scan all lines or lines with a given flag.

## State and persistence behavior
All declared state is in-memory and tied to `struct gpio_device` lifetime. Descriptor labels are RCU/SRCU-freed through `struct gpio_desc_label`. `gpio_array` is co-allocated with `struct gpio_descs` by `gpiod_get_array()` and caches masks for fast same-chip bitmap I/O. There is no persistent storage beyond firmware data consumed by the implementation.

## Dependencies and integration points
The header depends on Linux device, cdev, module, notifier, spinlock, SRCU, workqueue, GPIO consumer/driver, and pinctrl-facing types. It is included by the GPIO cdev/sysfs/OF/ACPI/shared implementation files and provides their private contract with the central gpiolib core.

## Risks and edge cases
Flag bit meanings are ABI-like within the GPIO core; mismatches break cdev notifications, IRQ safety checks, and line configuration. `gpio_device_get_chip()` style access is explicitly unsafe without SRCU, so users should prefer the guard pattern. The property suffix macro uses a caller-provided buffer and depends on the buffer being large enough. `gpio_array` fast-path layout assumes it immediately follows the descriptor pointer array allocated by `gpiod_get_array()`.

## Test signals
Compile coverage across GPIO core variants is essential. Runtime signals include successful hot-unplug without use-after-free, cdev line info matching descriptor flags, array fast path use only for eligible descriptors, correct line-state notifications, hog cleanup, and pinctrl/IRQ helpers observing the same flags as gpiolib core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpiolib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/Kconfig

## Purpose
This Kconfig file declares the common GPU buddy allocator option and its KUnit test option for the GPU driver subtree.

## Important APIs, types, and functions
It defines `GPU_BUDDY` as an internal boolean and `GPU_BUDDY_KUNIT_TEST` as a tristate test module/built-in option depending on `GPU_BUDDY && KUNIT`, defaulting to `KUNIT_ALL_TESTS`.

## Control flow
At configuration time, GPU and DRM memory managers can select `GPU_BUDDY` when they need the common page-based buddy allocator. If KUnit testing is enabled globally or selected explicitly, `GPU_BUDDY_KUNIT_TEST` controls building the allocator tests under `drivers/gpu/tests`.

## State and persistence behavior
The file has no runtime state. Its choices persist only in the kernel `.config` and determine which objects are compiled.

## Dependencies and integration points
`GPU_BUDDY` is selected by DRM options such as `DRM_BUDDY`; `GPU_BUDDY_KUNIT_TEST` integrates with KUnit and the GPU tests Makefile.

## Risks and edge cases
Because `GPU_BUDDY` is hidden, allocator users must select it correctly. Enabling tests without the allocator or KUnit is prevented by dependencies, but missing selects in downstream users would produce compile failures for `linux/gpu_buddy.h` symbols.

## Test signals
Configuration tests should verify that selecting DRM buddy users enables `GPU_BUDDY`, and KUnit builds should compile/run `gpu_buddy_test` for built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/Makefile

## Purpose
This top-level GPU Kbuild file orders common GPU objects and major GPU-related subdirectories.

## Important APIs, types, and functions
It builds `buddy.o` under `CONFIG_GPU_BUDDY`, unconditionally descends into `host1x/`, `drm/`, `vga/`, and `tests/`, and conditionally includes `ipu-v3/`, `trace/`, and `nova-core/`.

## Control flow
Kbuild link order is significant here: `buddy.o` is listed before subdirectories because GPU/DRM drivers may use the allocator, and `host1x/` precedes `drm/` because built-in Tegra DRM depends on host1x initialization ordering.

## State and persistence behavior
The file controls build composition only. It creates no runtime state.

## Dependencies and integration points
It integrates the common GPU buddy allocator with DRM and host1x consumers, and routes GPU memory tracing or Nova core builds based on their config symbols.

## Risks and edge cases
Changing link order can break built-in initialization dependencies. Removing `buddy.o` from the early position can produce unresolved symbols or late init failures for built-in DRM memory managers.

## Test signals
Build tests should cover built-in and module configurations for GPU buddy, Tegra/host1x plus DRM, and `CONFIG_GPU_BUDDY_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/buddy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/buddy.c

## Purpose
`buddy.c` implements the common GPU page-based buddy allocator used by DRM/TTM VRAM managers and other GPU memory users. It manages a byte-addressed aperture split into power-of-two blocks, supports allocations constrained by range, alignment, top-down preference, contiguity, and clear/dirty state, and returns allocated block lists to callers.

## Important APIs, types, and functions
Exported APIs are `gpu_buddy_init()`, `gpu_buddy_fini()`, `gpu_buddy_alloc_blocks()`, `gpu_buddy_block_trim()`, `gpu_buddy_reset_clear()`, `gpu_buddy_free_block()`, `gpu_buddy_free_list()`, `gpu_buddy_block_print()`, and `gpu_buddy_print()`. Internal helpers include `split_block()`, `__gpu_buddy_free()`, `__force_merge()`, `alloc_from_freetree()`, `__gpu_buddy_alloc_range_bias()`, `gpu_buddy_offset_aligned_allocation()`, `__gpu_buddy_alloc_range()`, and `__alloc_contig_try_harder()`. Blocks are allocated from a `kmem_cache`, and free blocks are stored in per-order red-black trees for clear and dirty memory.

## Control flow
Initialization validates size and chunk size, rounds size to chunk units, creates free-tree arrays, splits non-power-of-two apertures into root blocks, and inserts roots into dirty free trees. Allocation validates alignment and range, rounds or preserves size depending on flags, computes order/min-order, then repeatedly selects a block from a range-biased DFS, offset-aligned search, or free tree. Larger blocks are split until the target order is reached, chosen blocks are marked allocated, availability counters are updated, and oversized rounded allocations may be trimmed back with `gpu_buddy_block_trim()`. Freeing marks blocks clear or dirty according to flags, merges with a compatible free buddy where possible, and reinserts the merged block. Forced merge can coalesce dissimilar clear/dirty buddies when needed for larger allocations or teardown.

## State and persistence behavior
Allocator state lives in `struct gpu_buddy`: total size, available bytes, clear-available bytes, chunk size, max order, root block list, and `[clear|dirty][order]` free trees. Each `gpu_buddy_block` encodes offset, state, clear flag, and order in its header and stores parent/child, list, temporary DFS, and RB-tree links. State is volatile in kernel memory; callers persist any higher-level resource ownership outside this allocator.

## Dependencies and integration points
The implementation depends on `include/linux/gpu_buddy.h`, Linux RB-tree augmented callbacks, slab caches, bitmap/order helpers, `kmemleak_update_trace()`, KUnit failure hooks when enabled, and exported symbols consumed by DRM buddy wrappers, amdgpu VRAM management, i915/xe TTM managers, and GPU allocator tests.

## Risks and edge cases
Key risks are accounting drift in `avail`/`clear_avail`, merge behavior when buddies have dissimilar clear state, allocation rollback after partial splits, off-by-one range handling, `roundup_pow_of_two()` for large contiguous allocations, alignment search correctness for offset-zero blocks, mutation while iterating RB trees during forced merge, and callers freeing lists with the wrong clear/dirty flag. The allocator itself does not lock, so callers must serialize access. `gpu_buddy_fini()` assumes all allocations have been returned.

## Test signals
KUnit should cover init/fini with non-power-of-two sizes, invalid chunk sizes, simple and ranged allocations, top-down placement, contiguous fallback, offset-aligned small allocations, trimming, free-list clear/dirty marking, forced merge paths, allocation failure rollback, clear-available accounting, and final teardown assertions that all memory is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/buddy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/Kconfig

## Purpose
`drivers/gpu/drm/Kconfig` is the main Direct Rendering Manager configuration menu. It defines the core DRM option, common DRM helper subsystems, debugging and panic-screen features, memory-management helpers, and sources all individual DRM driver Kconfig files.

## Important APIs, types, and functions
Important symbols include `DRM`, `DRM_KMS_HELPER`, `DRM_CLIENT`, `DRM_TTM`, `DRM_EXEC`, `DRM_GPUVM`, `DRM_GPUSVM`, `DRM_BUDDY`, GEM DMA/SHMEM/VRAM/TTM helper options, `DRM_SCHED`, `DRM_PANIC*`, `DRM_RAS`, and debug options. The file sources driver menus such as `adp`, `amd/amdgpu`, `i915`, `xe`, `nouveau`, `virtio`, `vkms`, and many SoC display drivers.

## Control flow
Configuration starts with `menuconfig DRM`, which depends on DMA-capable non-emulated atomic support and selects shared infrastructure such as DMA-BUF, sync files, HDMI, I2C, KCMP, and video support. Inside `if DRM`, helper libraries and memory managers become available for drivers to select. The long source list imports each driver-specific menu in sorted order.

## State and persistence behavior
There is no runtime state. Selected symbols persist in the kernel configuration and drive which DRM core, helpers, and drivers are built.

## Dependencies and integration points
The file is the integration hub between DRM core, framebuffer emulation helpers, GPU memory management, KMS helpers, display helpers, panel/bridge subsystems, Rust helper selection, RAS generic netlink, and vendor/SoC driver Kconfigs. `DRM_BUDDY` selects the common `GPU_BUDDY` allocator.

## Risks and edge cases
Incorrect dependencies or selects can create invalid configs, such as helpers enabled without `MMU`, panic QR support without Rust/zlib support, or driver menus visible without required platform dependencies. Since many drivers rely on helper symbols being selected transitively, removing a select can break builds far from this file.

## Test signals
Use allmodconfig/allnoconfig/allyesconfig and targeted configs for DRM core without drivers, helper-only selections, panic/RAS/debug options, and driver menus such as ADP and amdgpu. Kconfig warnings about unmet direct dependencies are the main early signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/Makefile

## Purpose
This Makefile builds the DRM core object, helper libraries, memory-management components, tests, and all selected DRM drivers.

## Important APIs, types, and functions
It defines `drm-y` for core objects such as atomic, auth, bridge, connector, CRTC, framebuffer, GEM, ioctl, lease, modes, modeset lock, plane, prime, syncobj, vblank, VMA manager, and writeback. It conditionally adds client, compat, panel, OF/PCI, debugfs, privacy, accel, panic, draw, QR, and RAS objects. It builds helpers such as `drm_kms_helper.o`, `drm_dma_helper.o`, `drm_shmem_helper.o`, `drm_vram_helper.o`, `drm_ttm_helper.o`, `drm_gpusvm_helper.o`, `drm_exec.o`, `drm_gpuvm.o`, and `drm_buddy.o`, then descends into selected driver directories.

## Control flow
Kbuild composes `drm.o` when `CONFIG_DRM` is enabled, adds helper composite objects according to config symbols, then includes tests and driver subdirectories according to individual driver options. The file also sets local warning flags, dynamic-debug flags, optional DRM `-Werror`, and header self-test rules.

## State and persistence behavior
The Makefile has build-time state only. Runtime state is created by the compiled DRM modules and drivers.

## Dependencies and integration points
It integrates the DRM subsystem with Kbuild, dynamic debug, warning policy, memory managers, framebuffer helpers, acceleration helpers, and every vendor/SoC driver directory. It also includes header test generation through `KERNELDOC` and compiler syntax checks.

## Risks and edge cases
Object ordering and config-conditioned composite objects are sensitive: missing helper members cause unresolved symbols, and warning policy changes can fail CI when `CONFIG_DRM_WERROR` is enabled. Driver directory whitespace or missing spaces around `+=` entries can produce surprising Kbuild behavior. Header tests depend on self-contained headers and kernel-doc cleanliness.

## Test signals
Build signals include `make drivers/gpu/drm/`, allmodconfig, DRM built-in and module builds, selected helper-only configs, `CONFIG_DRM_HEADER_TEST`, `CONFIG_DRM_WERROR`, and representative driver selections such as `DRM_ADP`, `DRM_AMDGPU`, `DRM_I915`, and `DRM_XE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Kconfig

## Purpose
This Kconfig entry enables the Apple Display Pipe DRM driver for pre-DCP Apple display controllers, primarily the Apple Arm touchbar display pipe.

## Important APIs, types, and functions
It defines `DRM_ADP` as a tristate depending on `DRM`, `OF`, `ARM64`, and `ARCH_APPLE || COMPILE_TEST`. It selects KMS, bridge connector, display helper, KMS DMA, GEM DMA, panel bridge, videomode helpers, and MIPI DSI support.

## Control flow
When `DRM_ADP` is selected, Kbuild compiles both the display pipe DRM driver and its MIPI DSI host companion module through the ADP Makefile. If built as a module, the primary module name is documented as `adpdrm`.

## State and persistence behavior
The file has no runtime state; it persists only as kernel config selection.

## Dependencies and integration points
It integrates ADP with the DRM/KMS helper stack, DRM bridges/connectors, DMA-backed GEM buffers, panel bridges, videomode helpers, OF graph discovery, MIPI DSI, and Apple ARM64 platform support.

## Risks and edge cases
The dependencies intentionally restrict real use to Apple ARM64 while allowing compile testing. Missing helper selects would break ADP build or runtime bridge attachment. The help text is narrow to touchbar use even though compatible strings drive actual device matching.

## Test signals
Kconfig/build tests should cover `DRM_ADP=y` and `=m` on `ARCH_APPLE` and `COMPILE_TEST`, ensuring helper symbols are selected and both `adpdrm` and `adpdrm-mipi` objects build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Makefile

## Purpose
This Kbuild file composes the Apple Display Pipe DRM modules.

## Important APIs, types, and functions
It defines `adpdrm-y := adp_drv.o`, `adpdrm-mipi-y := adp-mipi.o`, and builds both `adpdrm.o` and `adpdrm-mipi.o` when `CONFIG_DRM_ADP` is enabled.

## Control flow
Kbuild emits two objects for the one Kconfig symbol: the main DRM/KMS platform driver and a companion MIPI DSI host/bridge platform driver. Component framework matching at runtime connects the two devices through OF graph data.

## State and persistence behavior
The file has build-time state only.

## Dependencies and integration points
It depends on `CONFIG_DRM_ADP` and integrates `adp_drv.c` with `adp-mipi.c`.

## Risks and edge cases
Because both modules are controlled by one symbol, systems need matching device-tree nodes for both sides or the main component bind can defer/fail. Renaming either source file without updating this Makefile breaks the build.

## Test signals
Build `CONFIG_DRM_ADP=y` and `=m`, confirm both objects are produced, and boot with Apple display pipe plus MIPI nodes to exercise component matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp-mipi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp-mipi.c

## Purpose
`adp-mipi.c` implements the Apple Display Pipe MIPI DSI host and bridge companion. It maps the MIPI MMIO registers, sends and receives DSI packets through command/payload FIFOs, exposes `mipi_dsi_host_ops`, and attaches the next DRM bridge found in the OF graph.

## Important APIs, types, and functions
The main private type is `struct adp_mipi_drv_private`, containing a `mipi_dsi_host`, local DRM bridge, next bridge pointer, and MMIO base. Important functions are `adp_dsi_gen_pkt_hdr_write()`, `adp_dsi_write()`, `adp_dsi_read()`, `adp_dsi_host_transfer()`, host `attach`/`detach`, `adp_dsi_bridge_attach()`, `adp_mipi_probe()`, and `adp_mipi_remove()`.

## Control flow
Probe allocates a managed DRM bridge container, maps the MIPI resource, initializes host and bridge metadata, stores driver data, and registers the MIPI DSI host. On DSI device attach, it resolves the downstream bridge from graph port 1, adds the local bridge, and registers a component so the master ADP DRM device can bind. Transfers create a DSI packet, write payload words to `DSI_GEN_PLD_DATA` while polling FIFO status, write the packet header to `DSI_GEN_HDR`, and optionally poll/read response payload words. Detach removes the component and bridge; remove unregisters the host.

## State and persistence behavior
State is limited to the platform device lifetime: MMIO base, host registration, local bridge registration, and `next_bridge`. FIFO state lives in hardware registers. There is no persistent state.

## Dependencies and integration points
The file depends on platform devices, OF graph bridge lookup, Linux component framework, `readl_poll_timeout()`, DRM bridge APIs, and MIPI DSI host APIs. It integrates with `adp_drv.c` through the component framework and with downstream panel/bridge drivers through `drm_bridge_attach()`.

## Risks and edge cases
FIFO polling timeouts can fail transfers, and the code assumes 32-bit payload packing and little-endian header conversion. There is no explicit DSI mode programming, lane setup, or power sequencing in this file, so it relies on surrounding hardware/firmware state. Component bind/unbind callbacks are empty, making ordering dependent on host attach and main driver bridge resolution. Attach failure must remove the bridge to avoid stale registration.

## Test signals
Probe should map `apple,h7-display-pipe-mipi`, register a DSI host, attach a downstream panel/bridge, and complete DCS write/read transfers. Fault signals include FIFO full/empty timeouts, missing graph bridge, component add failure, detach cleanup, and module unload after active DSI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp-mipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp_drv.c

## Purpose
`adp_drv.c` is the main Apple Display Pipe DRM/KMS driver. It creates a minimal atomic DRM device for the Apple touchbar display pipe, programs backend/frontend MMIO registers for a single XRGB8888 primary plane, handles vblank/page-flip events, builds an encoder/bridge/connector chain, and participates in component binding with the MIPI companion.

## Important APIs, types, and functions
The private state is `struct adp_drv_private`, embedding `struct drm_device`, one `drm_crtc`, encoder/connector/bridge pointers, backend/frontend MMIO bases, IRQs, a coherent mask buffer, and a pending vblank event. Important functions include `adp_open()`, `adp_drm_gem_dumb_create()`, `adp_plane_atomic_check/update/disable()`, `adp_crtc_atomic_enable/disable/flush()`, `adp_setup_crtc()`, `adp_setup_mode_config()`, `adp_parse_of()`, `adp_fe_irq()`, `adp_drm_bind()`, `adp_drm_unbind()`, `adp_probe()`, and `adp_remove()`.

## Control flow
Probe allocates a managed DRM device, maps named `be` and `fe` resources, reads `be`/`fe` IRQs, finds the remote OF graph node, and registers as a component master. Bind enables the FE FIFO, resolves the next bridge, initializes mode config, creates a primary plane and CRTC, allocates an encoder, attaches the bridge chain with `NO_CONNECTOR`, creates a bridge connector, initializes vblank, requests the FE IRQ, and registers the DRM device. Atomic plane updates program source/destination rectangles, stride, framebuffer DMA address, layer enables, scaling bypass, layer control, and pixel format. Atomic flush resizes/reallocates a coherent all-ones mask buffer for the current mode, writes its DMA address, triggers FIFO sync, and stores or sends page-flip events depending on vblank availability. FE IRQ handles vblank and sends deferred events once control bits indicate completion.

## State and persistence behavior
Runtime state is in `struct adp_drv_private` and hardware registers. GEM buffers are DMA-backed DRM objects; dumb buffers align height to 64 and compute size from pitch. The mask buffer is coherent DMA and is reallocated when mode dimensions change. No persistent storage exists.

## Dependencies and integration points
The file depends on DRM atomic/KMS helpers, GEM DMA helpers, framebuffer helpers, bridge connector APIs, OF graph/component framework, platform MMIO/IRQ resources, DMA coherent allocation, and MIPI/bridge devices supplied by `adp-mipi.c` and downstream panels. It exposes a DRM device named `adp`.

## Risks and edge cases
`adp_open()` refuses processes whose command starts with `X` to work around Xorg modesetting behavior, which is intentionally policy-like and brittle. `adp_crtc_atomic_flush()` does not check `dma_alloc_coherent()` failure before `memset()`, creating a potential null dereference. The mask buffer is not explicitly freed in unbind/remove except through resize paths. IRQ cleanup occurs after DRM shutdown, but request failure after setup needs managed state to unwind correctly. Only XRGB8888 and no scaling are supported, and MMIO programming assumes the hardware accepts the fixed register sequence.

## Test signals
Boot on matching `apple,h7-display-pipe` hardware, component bind with MIPI, modeset to the touchbar size, dumb-buffer creation with 64-line alignment, atomic page flips and vblank event delivery, open behavior from Xorg versus non-X clients, suspend/shutdown via `drm_atomic_helper_shutdown()`, IRQ handling, missing bridge/IRQ/resource probe failures, and DMA allocation fault injection for the mask buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Kconfig

## Purpose
This Kconfig menu controls AMD Audio CoProcessor support as an amdgpu subcomponent.

## Important APIs, types, and functions
It defines `DRM_AMD_ACP` as a boolean under the ACP configuration menu, depending on `DRM_AMDGPU`, selecting `MFD_CORE`, and selecting `PM_GENERIC_DOMAINS` when PM is enabled.

## Control flow
When enabled, the amdgpu Makefile includes `amdgpu_acp.o` and the ACP hardware file list. The option wires ACP IP support into amdgpu for APUs that use the ACP DMA engine for I2S-based ALSA audio.

## State and persistence behavior
There is no runtime state in the Kconfig file; the selection persists in `.config`.

## Dependencies and integration points
The option integrates AMD GPU display/device code with MFD and power-domain infrastructure and enables the ACP hardware code under `drivers/gpu/drm/amd/acp`.

## Risks and edge cases
ACP support is tied directly to `DRM_AMDGPU`; enabling it without the correct SoC/audio stack may build unused code, while disabling it can remove required I2S audio support on APUs. PM domain selection is conditional, so PM-disabled builds need separate compile coverage.

## Test signals
Build amdgpu with `DRM_AMD_ACP=y` and `n`, with and without PM, and boot ACP-capable APUs to confirm audio DMA device registration through amdgpu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Makefile

## Purpose
This Makefile defines the ACP hardware object list consumed by the amdgpu build.

## Important APIs, types, and functions
It sets `AMD_ACP_FILES := $(AMDACPPATH)/acp_hw.o`. There are no runtime functions in this file.

## Control flow
The amdgpu Makefile sets `AMDACPPATH := ../acp`, includes this file when `CONFIG_DRM_AMD_ACP` is enabled, and appends `$(AMD_ACP_FILES)` to `amdgpu-y`.

## State and persistence behavior
The file has only build-time variable state.

## Dependencies and integration points
It depends on the parent amdgpu Makefile defining `AMDACPPATH`. It integrates `acp_hw.o` into the monolithic `amdgpu.o` object rather than building a separate ACP module.

## Risks and edge cases
The relative path indirection must remain aligned with the parent Makefile. Renaming `acp_hw.c` or changing include order can make `AMD_ACP_FILES` empty or wrong.

## Test signals
Build `CONFIG_DRM_AMDGPU=y/m` with `CONFIG_DRM_AMD_ACP=y` and confirm `../acp/acp_hw.o` is part of `amdgpu.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/acp_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/acp_hw.c

## Purpose
`acp_hw.c` provides a small hardware initialization gate for AMD ACP support inside amdgpu. It checks whether the ACP block is configured for I2S mode and rejects unsupported Azalia mode for the relevant hardware version.

## Important APIs, types, and functions
The exported-to-amdgpu function is `amd_acp_hw_init(struct cgs_device *cgs_device, unsigned acp_version_major, unsigned acp_version_minor)`. It reads `mmACP_AZALIA_I2S_SELECT` through `cgs_read_register()` for ACP version 2.2 and compares against `ACP_MODE_I2S`.

## Control flow
Initialization defaults `acp_mode` to I2S. For ACP 2.2, it reads the hardware select register. If the resulting mode is not I2S, it returns `-ENODEV`; otherwise it returns success. Other versions are accepted without a register read in this file.

## State and persistence behavior
The file stores no persistent or long-lived runtime state. It only reads an MMIO-backed register through the CGS device abstraction.

## Dependencies and integration points
It depends on `acp_gfx_if.h`, `cgs_common.h`, and the amdgpu CGS register access interface. It is pulled into `amdgpu.o` when `DRM_AMD_ACP` is enabled and is expected to be called by amdgpu ACP integration code before exposing ACP audio functionality.

## Risks and edge cases
The version check is narrow: only 2.2 reads the mode register, so behavior for later versions relies on external code or defaults. A stale or inaccessible CGS device would make the register read path unsafe if callers do not ensure initialization. Returning `-ENODEV` for non-I2S mode is correct for I2S audio but must not be treated as a fatal GPU probe error by callers.

## Test signals
Unit or hardware tests should cover ACP 2.2 with I2S and Azalia register values, other version numbers, invalid CGS/register access paths, and amdgpu probe behavior when ACP init returns `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/acp_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/include/acp_gfx_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/include/acp_gfx_if.h

## Purpose
`acp_gfx_if.h` declares the ACP-to-amdgpu graphics interface used to initialize ACP hardware support.

## Important APIs, types, and functions
It includes `cgs_common.h` and declares `amd_acp_hw_init(struct cgs_device *cgs_device, unsigned acp_version_major, unsigned acp_version_minor)`.

## Control flow
The header has no executable control flow. It allows amdgpu ACP integration code to call the implementation in `acp_hw.c`.

## State and persistence behavior
No state is declared beyond the opaque `struct cgs_device` dependency.

## Dependencies and integration points
It depends on Linux types and AMD CGS common definitions. The include path is added by the amdgpu Makefile through `-I$(FULL_AMD_PATH)/acp/include`.

## Risks and edge cases
The prototype ties ACP initialization to the legacy CGS abstraction; changes to CGS types or ACP versioning need matching updates in both caller and implementation. Since this is a small interface header, missing include guards or path configuration would break amdgpu builds.

## Test signals
Build amdgpu with ACP enabled and compile callers that include this header. Runtime validation is covered by `amd_acp_hw_init()` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/include/acp_gfx_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Kconfig

## Purpose
This Kconfig file defines the AMDGPU DRM driver and related feature switches for older ASIC family support, userptr/HMM behavior, AMD ISP support, warning policy, and GCOV profiling, then sources AMD ACP, display, and KFD configuration.

## Important APIs, types, and functions
Key symbols are `DRM_AMDGPU`, `DRM_AMDGPU_SI`, `DRM_AMDGPU_CIK`, `DRM_AMDGPU_USERPTR`, `DRM_AMD_ISP`, `DRM_AMDGPU_WERROR`, and `GCOV_PROFILE_AMDGPU`. `DRM_AMDGPU` selects firmware loading, DRM client/helper/display infrastructure, scheduler, TTM, power, hwmon, I2C, backlight, interval tree, DRM buddy, suballocator, exec helper, panel quirks, and ACPI video/input dependencies when applicable.

## Control flow
Selecting `DRM_AMDGPU` exposes amdgpu as a tristate PCI DRM driver. Optional SI and CIK booleans enable support for older GCN families that can overlap with radeon, with module parameters documented for driver selection. Userptr selects HMM/MMU notifier support. ISP and ACP options are nested via sourced Kconfigs. Werror and GCOV alter build flags through the Makefile.

## State and persistence behavior
The file has no runtime state. Config choices persist in the kernel `.config` and affect driver object composition and runtime feature availability.

## Dependencies and integration points
It integrates amdgpu with PCI, DRM core/helpers, scheduler, TTM, GPU buddy, ACPI video/WMI, HMM, MFD/PM domains through sourced ISP/ACP options, AMD display core, and KFD compute support.

## Risks and edge cases
The SI/CIK split with radeon is configuration- and module-parameter-sensitive. Broad `select` usage can force dependencies into configs unexpectedly, especially ACPI video/WMI. GCOV adds size/runtime overhead. Werror is disabled for compile tests, but enabling it on development configs can turn benign warnings into hard failures.

## Test signals
Kconfig and build tests should cover amdgpu as built-in/module, SI/CIK on/off combinations with radeon, userptr/HMM, ACPI and non-ACPI configs, ISP/ACP toggles, GCOV profiling, and Werror development builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Makefile

## Purpose
This Makefile composes the very large `amdgpu.o` DRM driver from core KMS, memory-management, ASIC, display, media, power, reset, RAS, compute, ACP, ISP, and compatibility objects, while setting AMD-specific include paths and build flags.

## Important APIs, types, and functions
It sets `FULL_AMD_PATH`, display paths, `GCOV_PROFILE`, extensive `ccflags-y` include directories, local warning suppressions, optional `-Werror`, and starts `amdgpu-y` with `amdgpu_drv.o`. It then appends core objects (`amdgpu_device.o`, `amdgpu_ttm.o`, `amdgpu_vm.o`, `amdgpu_cs.o`, etc.), ASIC families, DF/GMC/UMC/IH/PSP/DCE/GFX/SDMA/MES/UVD/VCE/VCN/JPEG/VPE/UMSCH/ATHUB/SMUIO/reset/MCA/KFD bridge objects, optional KFD files, CGS, scheduler jobs, ACP, compat, VGA switcheroo, ACPI, HMM, powerplay, display core, ISP, and RAS objects.

## Control flow
Kbuild evaluates config-conditioned sections to decide which object files are included. If KFD is enabled, it includes the amdkfd Makefile and appends compute integration objects. If ACP is enabled, it adds `amdgpu_acp.o`, defines `AMDACPPATH`, includes the ACP Makefile, and appends `AMD_ACP_FILES`. If DC display is enabled, it includes the AMD display Makefile and appends display objects. Powerplay and RAS Makefiles are always included for their file lists. Finally, `obj-$(CONFIG_DRM_AMDGPU) += amdgpu.o` emits the module/built-in object.

## State and persistence behavior
The Makefile has build-time variable state only. Runtime state is distributed across the compiled amdgpu subsystems.

## Dependencies and integration points
It integrates amdgpu with AMD shared headers, ASIC register headers, power management, ACP, display core, KFD, RAS, DRM helpers, TTM, HMM, ACPI, compat ioctl support, and optional ISP. Include paths are central because many AMD subtrees share private headers.

## Risks and edge cases
The file is sensitive to object ordering, include path order, and conditional includes. Missing an object can manifest as unresolved symbols only for specific ASIC/config combinations. ACP, KFD, DC, powerplay, and RAS Makefile includes depend on parent variables being defined first. GCOV and Werror options alter build behavior significantly. Typographical errors in long object lists are easy to miss and can break only narrow configs.

## Test signals
Validation should include allmodconfig, amdgpu built-in/module, SI/CIK toggles, KFD enabled/disabled, DC enabled/disabled, ACP and ISP toggles, ACPI/compat/HMM configurations, RAS and powerplay linkage, GCOV builds, Werror builds, and representative ASIC smoke boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/Makefile -->
