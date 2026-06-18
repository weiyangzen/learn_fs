# subset-b-003758 research

This grouped report covers the requested DRM/TTM source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm`. Each file section is delimited with reconciliation markers and is intended to be split into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c

Purpose: Implements TTM's generic `drm_mm` backed range resource manager for memory types such as VRAM or aperture ranges. It allocates page ranges, records them in `struct ttm_range_mgr_node`, and installs/removes a `struct ttm_resource_manager` into a `ttm_device` memory-type slot.

Important APIs/types/functions: `struct ttm_range_manager` wraps `ttm_resource_manager`, `drm_mm`, and a spinlock. `ttm_range_man_alloc()` allocates a flex node, initializes the resource, selects best-fit or top-down insertion, and inserts one `drm_mm_node`. `ttm_range_man_free()` removes the node and finalizes the TTM resource. `ttm_range_man_intersects()` and `ttm_range_man_compatible()` implement placement-range filtering for eviction and reuse. `ttm_range_man_init_nocheck()` and `ttm_range_man_fini_nocheck()` are exported setup/teardown helpers.

Control flow: initialization allocates the manager, initializes `drm_mm` over `[0, p_size)`, installs the manager with `ttm_set_driver_manager()`, and marks it used. Allocation computes `lpfn`, initializes TTM accounting/LRU state, inserts the DRM MM node under the range-manager spinlock, then publishes the resource. Teardown marks the manager unused, evicts all BOs, tears down `drm_mm`, removes the driver manager pointer, and frees the wrapper.

State and persistence: State is in-memory only: range occupancy lives in `drm_mm`, resource usage/LRU state in the embedded manager, and the node start becomes `res->start`. There is no on-disk persistence.

Dependencies and integration points: Depends on DRM MM, TTM placement/resource APIs, `ttm_bo_evict_first()` through manager teardown, and the device manager table. Backends use this for memory types where a contiguous page range must be reserved.

Risks and test signals: Fragmentation and spinlock hold time are called out in the source. Allocation error paths must pair `ttm_resource_fini()` with `kfree()`. Boundary tests should cover `fpfn/lpfn`, top-down placement, eviction filtering, teardown with live BOs, and `drm_mm_takedown()` after all objects are evicted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c

Purpose: Provides the common TTM resource-management core: resource initialization/finalization, allocation/free dispatch, LRU and bulk-move maintenance, resource-manager iteration, usage/debug output, cgroup device-memory charging, and kmap iterators for IO memory.

Important APIs/types/functions: `ttm_resource_init()` and `ttm_resource_fini()` maintain resource fields, LRU membership, and manager usage. `ttm_resource_alloc()` and `ttm_resource_free()` dispatch to backend `man->func` hooks and integrate `dmem_cgroup` charging. `ttm_lru_bulk_move_*()` manages bulk LRU tail moves by memory type and BO priority. `ttm_resource_cursor_*()` and `ttm_resource_manager_first()/next()` implement robust LRU iteration around hitch entries and bulk-move cursor tracking. `ttm_resource_manager_init()`, `ttm_resource_manager_evict_all()`, `ttm_resource_manager_usage()`, and `ttm_resource_manager_debug()` provide manager lifecycle and diagnostics. Kmap helpers include `ttm_kmap_iter_iomap_init()` and `ttm_kmap_iter_linear_io_init()/fini()`.

Control flow: Allocation first charges a dmem pool if configured, invokes the concrete manager allocator, stores the returned pool in `res->css`, and attaches eligible resources to the BO's bulk move under `bdev->lru_lock`. Free removes bulk tracking, calls the backend free hook, clears the caller pointer, and uncharges. LRU moves route pinned or swapped resources to `bdev->unevictable`, otherwise to a priority LRU or bulk tail. Manager eviction repeatedly calls `ttm_bo_evict_first()` until no entries remain, then waits for outstanding move fences.

State and persistence: Persistent runtime state includes manager usage, per-priority LRU lists, unevictable list entries, bulk-move ranges, cursor hitch positions, eviction fences, resource bus mappings, and optional dmem cgroup charge handles. All state is in kernel memory and protected by `lru_lock`, manager locks, or reservation assertions.

Dependencies and integration points: Integrates TTM BO/resource/placement APIs, DRM reservation fences, DRM printer/debugfs, scatter-gather DMA, `io_mapping`, `iosys_map`, and Linux cgroup device-memory accounting. Resource backends such as range and system managers rely on this common code.

Risks and test signals: Main risks are LRU corruption, usage underflow, cursor invalidation during bulk moves, missing dmem uncharge on allocation failure, IO mapping leaks, and misuse of reservation/lru locks. Test signals include KUnit/exported-test coverage for allocation/free, eviction, iteration across priority lists, bulk move add/delete, cgroup charge failure, and linear IO map fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c

Purpose: Implements the minimal TTM system-memory manager. It provides resource objects for `TTM_PL_SYSTEM` without reserving an external address range.

Important APIs/types/functions: `ttm_sys_man_alloc()` allocates a plain `struct ttm_resource` and initializes it. `ttm_sys_man_free()` finalizes and frees it. `ttm_sys_manager_func` supplies the backend hooks. `ttm_sys_man_init()` configures `bdev->sysman`, sets `use_tt = true`, registers it for `TTM_PL_SYSTEM`, and marks it used.

Control flow: Device initialization calls `ttm_sys_man_init()`, which initializes core manager state with size `0` and installs it in the TTM manager table. Later allocations call the simple backend, which relies on `ttm_resource_init()` for common LRU/accounting behavior and carries no start-range allocation.

State and persistence: State lives in `bdev->sysman` and per-resource allocations. It does not maintain a range allocator or persistent metadata beyond common TTM manager usage and LRU lists.

Dependencies and integration points: Uses TTM device/resource/placement APIs and Linux slab allocation. It is the default system-memory path used by TTM BOs with translation tables.

Risks and test signals: The file is small; risk centers on pairing allocation/finalization and ensuring system resources are correctly treated as TT-backed. Tests should allocate/free system-placement BOs and verify manager registration, usage accounting, and LRU behavior through the common TTM resource code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c

Purpose: Owns TTM translation-table page storage: creation, initialization, population/unpopulation, swap-in/swap-out, backup/restore, global page-limit accounting, shrink debugfs support, and local kmap iteration over TT pages.

Important APIs/types/functions: `ttm_tt_create()` asks the driver to allocate a `ttm_tt` and sets flags based on BO type, zero allocation, external SG objects, and encrypted guest memory. `ttm_tt_init()`, `ttm_sg_tt_init()`, and `ttm_tt_fini()` manage page/dma-address arrays and swap/backup resources. `ttm_tt_populate()` enforces `pages_limit`/`dma32_pages_limit`, invokes driver or pool allocation, and handles swapin. `ttm_tt_unpopulate()`, `ttm_tt_swapout()`, `ttm_tt_swapin()`, `ttm_tt_backup()`, `ttm_tt_restore()`, and `ttm_tt_setup_backup()` implement reclaim paths. `ttm_kmap_iter_tt_init()` maps individual pages using `kmap_local_page_prot()`.

Control flow: BO creation calls `ttm_tt_create()` under reservation lock, then driver-provided creation calls into the init helpers. Population increments global page counters for non-external TT, triggers global swapout while limits are exceeded, allocates pages through the driver or pool, sets `PRIV_POPULATED`, clears backup state, and reloads swapped data when needed. Swapout creates a shmem file, copies pages to it, unpopulates the TT, stores `swap_storage`, and marks `SWAPPED`.

State and persistence: Runtime state is in `ttm->pages`, `ttm->dma_address`, `ttm->page_flags`, `swap_storage`, `backup`, and global atomic page counters. Swap and backup use shmem/file references as temporary kernel persistence for reclaim, not durable storage.

Dependencies and integration points: Integrates TTM pool, backup helper, BO/device callbacks, shmem, Linux module params, debugfs, memory-encryption detection, DRM cache protection helpers, and KUnit/test exports. It is shared by all TTM drivers that use TT-backed BOs.

Risks and test signals: Critical risks are counter imbalance on failure, swapped/backup flag inconsistency, missing `fput()`, encrypted-memory handling, external SG page-directory layout, and copy failures during swapin/out. Test signals include page-limit pressure, driver callback failure injection, external and external-mappable BOs, DMA32 pools, swap round trips, backup restore, and kmap iterator correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig

Purpose: Defines the `DRM_TVE200` build option for the Faraday TV Encoder TVE200 DRM driver.

Important APIs/types/functions: The option is a tristate named "DRM Support for Faraday TV Encoder TVE200". It depends on `DRM`, `CMA`, `ARM || COMPILE_TEST`, and `OF`; it selects `DRM_BRIDGE`, `DRM_CLIENT_SELECTION`, `DRM_PANEL_BRIDGE`, `DRM_KMS_HELPER`, and `DRM_GEM_DMA_HELPER`.

Control flow: Kconfig selection controls whether the Makefile emits `tve200_drm.o` built-in, as a module, or not at all. The help text states that module builds are named `tve200_drm`.

State and persistence: No runtime state; it is build-time configuration metadata.

Dependencies and integration points: Captures the driver's need for device-tree platform probing, CMA-backed DMA GEM buffers, bridge/panel integration, and KMS helpers.

Risks and test signals: Build coverage should include ARM and `COMPILE_TEST`, built-in and module builds, and configs with panel/bridge helpers enabled through selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile

Purpose: Builds the TVE200 DRM module from its two source objects.

Important APIs/types/functions: `tve200_drm-y` includes `tve200_display.o` and `tve200_drv.o`; `obj-$(CONFIG_DRM_TVE200)` emits `tve200_drm.o`.

Control flow: Kernel kbuild aggregates display-pipe code and platform-driver code into one driver object when `DRM_TVE200` is enabled.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Kconfig selecting the required DRM helper libraries. The build list reflects the split between hardware display programming and probe/lifecycle logic.

Risks and test signals: Build tests should catch missing object additions if new TVE200 source files are introduced, and module naming must match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c

Purpose: Implements TVE200's simple display pipe, vblank interrupt handler, mode validation, framebuffer address update, and register programming for supported RGB/YUV formats and fixed TV-class resolutions.

Important APIs/types/functions: `tve200_irq()` handles TVE200 interrupts and toggles vblank trigger position to work around level-like interrupt behavior. `tve200_display_check()` validates supported modes, dword-aligned base addresses, exact pitch, and format-change constraints. `tve200_display_enable()` resets hardware, enables clocks, programs `TVE200_CTRL` format/resolution/bus flags, and starts vblank. `tve200_display_update()` writes Y/U/V frame base registers and handles vblank events. `tve200_display_init()` creates the `drm_simple_display_pipe` with supported formats.

Control flow: Atomic check rejects unsupported modes or framebuffer layouts. Enable prepares the TVE clock, resets the block with retry sleeps, builds control bits from mode/connector bus flags/DRM fourcc, writes the control register, and enables vblank. Plane updates write framebuffer DMA addresses and arm/send events under `event_lock`. Disable turns off vblank, clears control, asserts reset, and disables the clock.

State and persistence: State is in hardware registers, `priv->pipe`, connector display info, and DRM CRTC event/vblank state. No durable persistence exists.

Dependencies and integration points: Integrates DRM simple KMS pipe, GEM DMA framebuffer helpers, panel bridge connector data, Linux clocks, MMIO accessors, and DRM vblank core. It relies on register constants and private device state from `tve200_drm.h`.

Risks and test signals: Risks include hard-coded NTSC/noninterlace choices, reset timeout leaving the clock enabled, pitch limitations, YUV plane address programming, and vblank IRQ toggling correctness. Test signals include atomic mode validation for all supported resolutions/formats, vblank event delivery, IRQ storm resistance, framebuffer alignment rejection, and suspend/remove shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h

Purpose: Declares TVE200 register offsets/bitfields, the driver private structure, and cross-file prototypes for the TVE200 DRM driver.

Important APIs/types/functions: Defines frame base, interrupt, control, reset, burst, retry, format, resolution, endian, YCbCr ordering, vblank trigger, BGR, and enable bits. `struct tve200_drm_dev_private` stores `drm`, connector/panel/bridge, simple display pipe, mapped regs, peripheral clock, and TVE pixel clock. Prototypes include `tve200_display_init()` and `tve200_irq()`.

Control flow: The header drives control-flow decisions in display and probe files by encoding how register fields map to DRM modes, bus flags, and formats.

State and persistence: It declares runtime state shape but stores no state itself. The private struct is allocated per platform device.

Dependencies and integration points: Includes `drm_simple_kms_helper` and Linux IRQ return types. It ties the display implementation to platform lifecycle code.

Risks and test signals: Bitfield mistakes directly affect hardware programming. Tests are mostly hardware or register-trace based: verify control values for RGB/YUV formats, interrupt mask/clear bits, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c

Purpose: Provides TVE200 platform-driver probe/remove/shutdown, DRM driver registration, mode-config setup, bridge/panel discovery, clocks/MMIO/IRQ acquisition, and fbdev client setup.

Important APIs/types/functions: `tve200_modeset_init()` configures mode limits, finds a panel/bridge, creates a panel bridge, initializes the display pipe, attaches the bridge, initializes vblank, resets mode config, and starts polling. `tve200_probe()` allocates private and DRM device state, enables PCLK, gets TVE clock, maps registers, requests IRQ, initializes modeset, registers DRM, and starts a default RGB565 client. `tve200_remove()` unregisters and cleans up. `tve200_drm_driver` uses GEM DMA and fbdev DMA helper ops.

Control flow: Probe is a staged resource-acquisition sequence with unwind labels for PCLK and DRM device references. Modeset init removes the panel bridge and cleans mode config on failure. Remove unregisters DRM, atomically shuts down KMS, removes panel bridge, cleans mode config, disables PCLK, and drops the DRM reference.

State and persistence: Runtime state lives in `drm->dev_private`, mapped registers, clocks, bridge/panel references, and DRM mode objects. No persistent storage exists.

Dependencies and integration points: Integrates platform bus, OF matching (`faraday,tve200`), DRM atomic/KMS helpers, panel bridge, GEM DMA, fbdev DMA, vblank, Linux clocks, IRQ, and ioremap helpers.

Risks and test signals: Risks include requiring a panel bridge only, clock unwind correctness, panel bridge cleanup, shutdown ordering, and default format compatibility. Tests should cover probe deferral/errors, module load/unload, DT binding with panel, IRQ request failure, and atomic shutdown on remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig

Purpose: Defines the Rust `DRM_TYR` option for ARM Mali CSF-based GPU experimentation.

Important APIs/types/functions: The option is tristate, depends on `DRM=y`, `RUST`, `ARM || ARM64 || COMPILE_TEST`, `!GENERIC_ATOMIC64`, and `COMMON_CLK`, and defaults to `n`. Help text states it targets Mali/Immortalis Valhall Gxxx CSF GPUs, excluding non-CSF G68/G78, and warns that it is work in progress.

Control flow: Enabling this option allows kbuild to compile the Rust `tyr` module.

State and persistence: Build-time metadata only.

Dependencies and integration points: Captures Rust kernel support, DRM built-in requirement, clock support, and architecture constraints tied to IOMMU page-table assumptions.

Risks and test signals: Build tests should cover Rust-enabled ARM64 and `COMPILE_TEST` configs, plus disabled cases where `DRM` is modular or Rust is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile

Purpose: Connects the Tyr Rust driver to kbuild.

Important APIs/types/functions: `obj-$(CONFIG_DRM_TYR) += tyr.o` builds the Rust module when selected.

Control flow: The Rust root module is `tyr.rs`, which kbuild compiles into `tyr.o`.

State and persistence: No runtime state.

Dependencies and integration points: Depends on the kernel Rust build system and the Kconfig option.

Risks and test signals: Build failures will surface when Rust module naming or source lists change. Module build tests are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs

Purpose: Implements Tyr's Rust platform and DRM driver glue for Mali Valhall CSF devices. It probes clocks/regulators/MMIO, performs early GPU reset and L2 power-on, reads GPU identity, creates a DRM device, and exposes a Panthor-compatible DRM driver name and ioctl.

Important APIs/types/functions: `TyrPlatformDriverData` owns a foreign-owned DRM device reference. `TyrDrmDeviceData` stores the platform device, clock/regulator mutexes, and `GpuInfo`. `issue_soft_reset()` writes `GPU_CMD_SOFT_RESET` and polls reset completion. The OF table matches `rockchip,rk3588-mali` and `arm,mali-valhall-csf`. `impl platform::Driver` performs probe. `impl drm::Driver` declares driver data/file/object types and the `PANTHOR_DEV_QUERY` ioctl.

Control flow: Probe gets and enables core/stacks/coregroup clocks, obtains enabled `mali` and `sram` regulators, maps 2 MiB MMIO, issues a soft reset, powers on L2, reads/logs GPU info, initializes DRM device data, creates the DRM device, and registers it. `PinnedDrop` for device data disables clocks.

State and persistence: State is in Rust-owned `ARef`s, pinned mutex-protected clock/regulator holders, devres MMIO, and immutable GPU info read at probe. No durable persistence exists.

Dependencies and integration points: Uses kernel Rust abstractions for platform devices, DRM, ioctls, clocks, regulators, devres IO memory, polling, `Arc`, and mutexes. User-space compatibility intentionally uses the `panthor` driver name and Panthor UAPI query.

Risks and test signals: The driver is incomplete and may leak semantic references to Panthor. Risks include probe unwind after partial clock enable, regulator requirements on boards without supplies, reset timeout, and lack of runtime PM/scheduler/MMU. Test signals are Rust build, probe on matching DT, successful `PANTHOR_DEV_QUERY`, reset/L2 poll success, and clock disable on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs

Purpose: Defines per-open DRM file data and implements the Panthor-compatible device-query ioctl for Tyr.

Important APIs/types/functions: `TyrDrmFileData` is an empty per-file struct. `impl drm::file::DriverFile` allocates it on open. `TyrDrmFileData::dev_query()` handles `DRM_PANTHOR_DEV_QUERY_GPU_INFO`; with `pointer == 0` it returns the required size, otherwise it writes `ddev.gpu_info` to the user pointer via `UserSlice`.

Control flow: Open allocates pinned file data. The ioctl validates query type, either reports size or copies the stored GPU info. Unknown query types return `EINVAL`.

State and persistence: Per-file state is currently empty; query data is read from the DRM device's stored `GpuInfo`.

Dependencies and integration points: Integrates Rust DRM file abstractions, UAPI Panthor structs, and safe user-copy helpers. It is registered by `driver.rs`.

Risks and test signals: Risks include not validating that user-provided size is sufficient before writing and only supporting one query type. Test with zero pointer size queries, valid copyout, invalid query type, too-small user buffers, and repeated opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gem.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gem.rs

Purpose: Provides the minimal Tyr GEM object driver-data type required by the Rust DRM driver.

Important APIs/types/functions: `TyrObject` is an empty pinned driver object. `impl gem::DriverObject` binds it to `TyrDrmDriver` and defines `new()` returning an empty object.

Control flow: DRM GEM object creation calls `new()`, which initializes no additional state.

State and persistence: No Tyr-specific GEM state exists in this file.

Dependencies and integration points: Depends on Rust DRM GEM abstractions and the driver type from `driver.rs`.

Risks and test signals: This is a placeholder; real memory management, MMU mapping, and shrink/eviction behavior are absent. Tests are limited to build/object-construction paths until GEM ioctls are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs

Purpose: Reads and exposes Mali GPU identity/features for Tyr, logs a human-readable model summary, decodes GPU IDs, and powers on the L2 block.

Important APIs/types/functions: `GpuInfo` transparently wraps `uapi::drm_panthor_gpu_info` and implements `AsBytes` for copyout. `GpuInfo::new()` reads identity, feature, thread, coherency, present-mask, and address-space registers. `GpuInfo::log()` prints model/features/presence masks. `va_bits()` and `pa_bits()` decode MMU feature widths. `GpuId::from(u32)` extracts architecture/product/version fields. `l2_power_on()` writes `L2_PWRON_LO` and polls `L2_READY_LO`.

Control flow: Probe calls `l2_power_on()` after reset and then `GpuInfo::new()`. GPU info is copied to userspace by `file.rs`. Logging maps known arch/product to `g610`, otherwise `unknown`.

State and persistence: GPU info is a snapshot captured at probe and stored in the DRM device data. No ongoing state is updated here.

Dependencies and integration points: Uses register constants from `regs.rs`, Rust devres IO access, polling, Panthor UAPI layout, and bitfield helpers.

Risks and test signals: Risks include stale or incomplete texture feature reporting, only one known model, assuming low/high present registers, and L2 poll timeout. Test signals include register-read fault propagation, correct UAPI byte layout, known GPU ID decoding, and behavior on unknown model IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs

Purpose: Defines Tyr's strongly typed 32-bit register accessor wrapper and the subset of Mali GPU register offsets/bit constants needed by reset, L2 power, and GPU-info queries.

Important APIs/types/functions: `Register<const OFFSET: usize>` has `read()` and `write()` methods using devres `IoMem` access. Constants cover GPU identity/features, IRQ status/clear/mask, soft/hard reset command, thread/texture/coherency features, present masks, L2 power/ready/transition/active registers, MCU control/status, job IRQ, and MMU IRQ.

Control flow: Higher-level code passes a bound device and devres MMIO object to each register accessor. Reads and writes can return errors if the devres access fails.

State and persistence: No state is stored here; constants encode hardware layout.

Dependencies and integration points: Uses Rust kernel IO traits, bit helpers, and the `IoMem` alias from `driver.rs`.

Risks and test signals: Incorrect offsets or bit definitions break hardware bring-up. The TODO notes a future register macro with 64-bit support. Tests should compare offsets against the C driver/spec, validate soft-reset and L2 bits, and cover access-error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/tyr.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/tyr.rs

Purpose: Rust module root for the Tyr DRM platform driver.

Important APIs/types/functions: Declares submodules `driver`, `file`, `gem`, `gpu`, and `regs`, imports `TyrPlatformDriverData`, and uses `kernel::module_platform_driver!` to register module metadata and platform-driver type.

Control flow: Kernel module initialization and exit are generated by the macro; probe/remove behavior is delegated to the `platform::Driver` implementation in `driver.rs`.

State and persistence: No state in this file beyond module registration metadata.

Dependencies and integration points: Integrates with the Rust kernel module and platform-driver infrastructure.

Risks and test signals: Build and module load/unload are the core tests. Metadata must stay aligned with Kconfig and driver naming expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/tyr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig

Purpose: Defines the `DRM_UDL` option for USB DisplayLink KMS adapters.

Important APIs/types/functions: The tristate depends on `DRM`, `USB`, `USB_ARCH_HAS_HCD`, and `MMU`; it selects `DRM_CLIENT_SELECTION`, `DRM_GEM_SHMEM_HELPER`, and `DRM_KMS_HELPER`.

Control flow: Enables building the `udl` module/driver.

State and persistence: Build-time metadata only.

Dependencies and integration points: Captures the driver's reliance on USB host support, MMU, shmem GEM, KMS helpers, and client setup.

Risks and test signals: Build matrix should include module and built-in variants, USB-enabled configs, and `COMPILE_TEST`-style coverage where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile

Purpose: Aggregates the UDL driver object list for kbuild.

Important APIs/types/functions: `udl-y` includes `udl_drv.o`, `udl_edid.o`, `udl_main.o`, `udl_modeset.o`, and `udl_transfer.o`; `obj-$(CONFIG_DRM_UDL) := udl.o`.

Control flow: Kbuild links USB lifecycle, EDID, URB management, modeset, and transfer compression code into one UDL module.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the module's source-level responsibilities and Kconfig option.

Risks and test signals: Build tests should catch missing object entries if features are split into new files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.c

Purpose: Implements the USB driver and DRM device registration lifecycle for DisplayLink adapters.

Important APIs/types/functions: `udl_usb_probe()` creates the managed DRM device, initializes hardware/modeset, registers DRM, and starts DRM client setup. `udl_usb_disconnect()` unplugs DRM and drops USB URBs. Suspend/resume hooks coordinate DRM mode-config helper suspend/resume and pending URB synchronization. `udl_usb_reset_resume()` reselects the standard channel before resume. The DRM driver uses shmem GEM and fbdev shmem helper ops.

Control flow: USB probe calls `udl_driver_create()`, which allocates `struct udl_device` via `devm_drm_dev_alloc()`, calls `udl_init()`, and stores it with `usb_set_intfdata()`. Disconnect calls `drm_dev_unplug()` before freeing USB resources so userspace sees device removal.

State and persistence: State is in managed `struct udl_device`, USB interface data, DRM mode objects, and URB pool initialized elsewhere. No durable persistence exists.

Dependencies and integration points: Integrates USB core matching DisplayLink vendor-defined interfaces, DRM atomic/GEM shmem helpers, modeset helper suspend/resume, and client setup.

Risks and test signals: Risks include disconnect during active transfers, suspend timeout, reset-resume channel failure, and lack of product-ID-specific matching. Test signals include hotplug/unplug under page flips, suspend/resume with pending URBs, reset resume, and DRM unplug behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h

Purpose: Declares UDL driver constants, device/URB structures, helpers, and cross-file prototypes.

Important APIs/types/functions: `struct urb_node` connects an URB to its UDL device and free-list entry. `struct urb_list` tracks available URBs with a spinlock, waitqueue, counts, and buffer size. `struct udl_device` embeds `drm_device`, SKU pixel limit, primary plane, CRTC, encoder, connector, and URB pool. Prototypes cover modeset, EDID connector init, URB get/submit/sync/completion, init/drop, protocol rendering, and channel selection.

Control flow: Other UDL files share one concrete `struct udl_device`, with `to_udl()` converting from DRM device to driver container and `udl_to_usb_device()` resolving the USB device.

State and persistence: Describes all major UDL runtime state: DRM objects, pixel limit, and URB pool.

Dependencies and integration points: Includes Linux USB and DRM plane/CRTC/connector/framebuffer headers.

Risks and test signals: Structure lifetime spans USB disconnect and DRM unplug, so tests should exercise URB waiters, connector cleanup, and access through `to_udl()` after unplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c

Purpose: Reads monitor EDID over DisplayLink USB vendor control transfers and provides probe/read helpers for the DRM connector.

Important APIs/types/functions: `udl_read_edid_block()` reads each EDID byte by issuing a USB control message and storing `read_buff[1]`. `udl_probe_edid()` reads the EDID header and treats all-zero data as disconnected. `udl_edid_read()` delegates to `drm_edid_read_custom()`.

Control flow: Connector detect calls `udl_probe_edid()`. Mode enumeration calls `udl_edid_read()`, which repeatedly invokes the block reader. The block reader uses `drm_dev_enter()/exit()` to avoid USB access after unplug.

State and persistence: EDID is read on demand and not cached here.

Dependencies and integration points: Integrates Linux USB control transfers, DRM EDID helpers, and UDL USB-device resolution.

Risks and test signals: Byte-at-a-time control reads are slow and sensitive to disconnects. Risks include short reads, all-zero false disconnect, and USB error handling. Test hotplug, no-monitor, corrupt/short EDID, unplug during EDID read, and multi-block EDID modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h

Purpose: Declares the UDL EDID helper API.

Important APIs/types/functions: Exposes `udl_probe_edid(struct udl_device *)` and `udl_edid_read(struct drm_connector *)` with forward declarations for DRM connector, DRM EDID, and UDL device.

Control flow: Included by modeset code to perform connector detection and mode enumeration.

State and persistence: No state.

Dependencies and integration points: Lightweight interface between `udl_modeset.c` and `udl_edid.c`.

Risks and test signals: Header must stay in sync with implementation signatures; compile coverage catches drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c

Purpose: Handles UDL device initialization, vendor-descriptor parsing, channel selection, reusable USB URB pool allocation/completion/submission/synchronization, and USB resource teardown.

Important APIs/types/functions: `udl_parse_vendor_descriptor()` reads descriptor `0x5f` and extracts SKU pixel limit key `0x0200`. `udl_select_std_channel()` sends the fixed standard-channel vendor command. `udl_alloc_urb_list()` allocates coherent bulk URBs, shrinking buffer size on failure. `udl_get_urb()` waits for an available URB. `udl_submit_urb()` submits a payload and requeues on error. `udl_sync_pending_urbs()` waits for all URBs to return. `udl_init()` sets DMA device, descriptor defaults, channel, URBs, and modeset. `udl_drop_usb()` frees URBs.

Control flow: Init sets a default FullHD-ish pixel limit, optionally overrides from firmware descriptor, selects the channel, builds a pool of 20 URBs up to `MAX_TRANSFER`, and initializes KMS. Completion returns URBs to the free list under spinlock and wakes waiters. Free waits for all URBs to be available before releasing coherent buffers and URB nodes.

State and persistence: Runtime state is the SKU pixel limit and URB pool (`count`, `available`, `size`, free list, waitqueue). No durable persistence exists.

Dependencies and integration points: Uses USB descriptors/control/bulk URBs, DRM logging, DMA-device setup for buffer sharing, and `udl_modeset_init()`.

Risks and test signals: Risks include URB pool deadlock on disconnect, timeout under heavy damage upload, descriptor parsing accepting bogus lengths, and fallback buffer sizing. Test descriptor variants, allocation pressure, USB submit errors, sync timeout, suspend/resume, and teardown with in-flight URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c

Purpose: Implements UDL atomic modesetting: DisplayLink register command generation, damage upload from shadow framebuffers, primary plane, CRTC enable/disable, connector detect/modes, mode limits, and KMS object initialization.

Important APIs/types/functions: Register-command helpers produce `UDL_MSG_BULK` packets. `udl_lfsr16()` converts timing values to hardware LFSR counters. `udl_set_display_mode()` maps DRM mode timings to DisplayLink registers. `udl_handle_damage()` renders each damaged line through `udl_render_hline()`. Plane helper functions use DRM shadow-plane helpers and damage iterators. CRTC enable sends color depth, base addresses, display mode, blank on, unlock, and dummy render; disable sends powerdown. Connector helpers use UDL EDID reads and detection. `udl_modeset_init()` creates mode config, primary plane, CRTC, encoder, and VGA connector.

Control flow: Atomic update begins CPU access to framebuffer, enters DRM device, iterates damage clips, and sends compressed URB command streams. Atomic enable/disable each allocate one URB and submit a register sequence. Mode validation enforces `sku_pixel_limit` if present.

State and persistence: State lives in DRM plane/CRTC/connector objects, shadow plane map, hardware registers, and the UDL URB pool. Mode programming is sent to device but not persisted by the driver.

Dependencies and integration points: Integrates DRM atomic helpers, damage helpers, GEM shmem/shadow helpers, EDID helpers, DisplayLink protocol constants, and URB submission from `udl_main.c`.

Risks and test signals: Risks include ignored return values inside damage loop, CPU-access direction ambiguity, LFSR timing mistakes, fixed 16bpp hardware programming despite XRGB8888 input conversion, and mode-limit mismatches. Tests should cover damage clips, full-screen updates, 16/32bpp conversion, mode enable/disable, EDID hotplug, oversized modes, and USB unplug during atomic update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_modeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h

Purpose: Defines DisplayLink bulk message command codes and register numbers used by UDL modeset and transfer code.

Important APIs/types/functions: Constants include `UDL_MSG_BULK`, register-write command, raw/RLE/copy framebuffer commands for 8/16 bpp, color-depth values, timing registers, blank modes, framebuffer base-address registers and masks, and video-register lock/unlock values.

Control flow: `udl_modeset.c` and `udl_transfer.c` compose command buffers using these constants before submitting URBs.

State and persistence: No state; hardware protocol definition only.

Dependencies and integration points: Uses Linux `GENMASK` via `linux/bits.h`.

Risks and test signals: Protocol mistakes cause display corruption or blanking. Test by tracing command streams for mode set, blank, base address, and encoded damage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c

Purpose: Encodes horizontal framebuffer spans into DisplayLink 16bpp command streams and submits them through reusable URBs.

Important APIs/types/functions: `pixel32_to_be16()` converts XRGB8888-style pixels to RGB565 big-endian. `get_pixel_val16()` reads 16bpp or converted 32bpp source pixels. `udl_compress_hline16()` emits `UDL_CMD_WRITERLX16` commands combining raw and repeat spans with a 256-pixel protocol limit. `udl_render_hline()` repeatedly compresses a line segment, submits full URBs, fetches new URBs, and returns the updated buffer pointer.

Control flow: The caller supplies source offsets, device framebuffer offset, byte width, and current URB/buffer pointers. Compression advances source pixels and command pointer until either the line is complete or the command buffer fills. Full buffers are submitted immediately and replaced with new URBs.

State and persistence: No durable state; transient state is source pointer, device address, command pointer, and current URB.

Dependencies and integration points: Depends on UDL protocol constants, URB helpers from `udl_main.c`, and modeset damage upload from `udl_modeset.c`.

Risks and test signals: Risks include unaligned 16/32-bit reads, command-buffer boundary errors, run-length count encoding off-by-one, conversion correctness, and partial failure leaving URBs completed/submitted correctly. Tests should compare encoded output for solid, alternating, and random lines; exercise buffer-boundary fills; and validate 16bpp/32bpp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Kconfig

Purpose: Defines the `DRM_V3D` option for Broadcom V3D 3.x and newer GPUs.

Important APIs/types/functions: The tristate depends on Broadcom/Raspberry Pi architectures or `COMPILE_TEST`, `DRM`, `COMMON_CLK`, and `MMU`; it selects `DRM_SCHED` and `DRM_GEM_SHMEM_HELPER`.

Control flow: Enables building the V3D render driver and its scheduler/shmem infrastructure.

State and persistence: Build-time metadata only.

Dependencies and integration points: Reflects runtime dependencies on GPU scheduler, GEM shmem, clocks, and MMU-backed GPU virtual addressing.

Risks and test signals: Build coverage should include supported SoC architectures, `COMPILE_TEST`, debugfs on/off, and transparent hugepage variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile

Purpose: Lists V3D driver objects for kbuild.

Important APIs/types/functions: Core objects include BO, driver, fence, GEM, IRQ, MMU, perfmon, trace points, scheduler, sysfs, and submit code. `v3d_debugfs.o` is conditional on `CONFIG_DEBUG_FS`. `obj-$(CONFIG_DRM_V3D)` emits `v3d.o`; trace points get `-I$(src)`.

Control flow: Kbuild links all functional slices into one DRM render driver.

State and persistence: No runtime state.

Dependencies and integration points: Shows integration with files outside this work item (`v3d_sched.c`, `v3d_submit.c`, `v3d_sysfs.c`, trace points).

Risks and test signals: Build tests should catch missing object dependencies and debugfs conditional coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c

Purpose: Implements V3D GEM buffer-object creation, lifetime, GPU VA allocation, page-table insertion/removal, PRIME import completion, CPU vmap helpers, and BO-related ioctls.

Important APIs/types/functions: `v3d_create_object()` allocates `struct v3d_bo` and installs object funcs. `v3d_bo_create_finish()` pins shmem pages, allocates a GPU VA range in `v3d->mm` with 4K/64K/1M alignment, updates stats, and inserts PTEs. `v3d_free_object()` unmaps vaddr, removes PTEs, drops stats and DRM MM node, marks pages dirty, and frees shmem. Ioctls cover create, mmap offset, GPU offset, and wait.

Control flow: Userspace create aligns size, creates shmem, finishes GPU mapping, returns GPU offset and GEM handle. PRIME import uses the shmem import helper and then performs the same finish path. Wait ioctl converts nanosecond timeout to jiffies, waits on the GEM reservation object, and decrements timeout for restart semantics.

State and persistence: BO state includes shmem pages/sgt, DRM MM node, optional kernel vaddr, stats counters, and GPU page-table entries. No durable persistence.

Dependencies and integration points: Integrates DRM GEM shmem, DRM MM, dma-buf PRIME, V3D MMU, VMA node mmap offsets, and reservation waiting.

Risks and test signals: Risks include GPU VA leaks on finish failure, PTE/DRM MM mismatch, imported buffer assumptions, timeout semantics, and pages dirty tracking. Tests should cover create/free, PRIME import failure, mmap/get-offset ioctls, wait interrupted/timeout cases, and hugepage alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c

Purpose: Provides V3D debugfs files for register dumps, hardware identity, BO stats, measured clock, and DRM MM state.

Important APIs/types/functions: Register definition arrays gate hub/GCA/core/CSD registers by V3D generation. `v3d_v3d_debugfs_regs()` dumps applicable registers. `v3d_v3d_debugfs_ident()` prints revision/features/core topology. `v3d_debugfs_bo_stats()` reports allocation counters. `v3d_measure_clock()` configures a performance counter, sleeps one second, and reports MHz. `v3d_debugfs_mm()` prints `drm_mm`. `v3d_debugfs_init()` registers files.

Control flow: DRM debugfs open invokes each show callback with a `drm_debugfs_entry`; callbacks resolve `v3d_dev`, read registers under no explicit runtime PM guard, and print seq output.

State and persistence: Read-only diagnostics over live registers and in-memory stats/MM allocator.

Dependencies and integration points: Uses DRM debugfs, seq_file, V3D register macros, bo locks, and MM lock.

Risks and test signals: Risks include reading registers when device is powered off/unplugged, generation gating mistakes, and measure_clock perturbing perf counters. Test by reading all files on supported generations and under active workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c

Purpose: Main V3D DRM platform driver: parameter ioctls, file open/close, fdinfo stats, DRM ioctl table, platform probe/remove, MMIO/clock/reset setup, generation detection, and module registration.

Important APIs/types/functions: `v3d_get_param_ioctl()` exposes register-backed and capability parameters. `v3d_open()` allocates per-file stats and scheduler entities for all queues, then initializes perfmon xarray. `v3d_postclose()` tears them down. `v3d_get_stats()` reads seqcount-protected stats for fdinfo. Probe maps hub/core/SMS/GCA/bridge regs, enables clock, configures DMA mask from MMU debug, reads hardware generation/cores/revision, initializes perfmon, reset, scratch page, GEM, IRQ, DRM, and sysfs.

Control flow: Probe is staged with unwinds for DRM unregister, IRQ disable, GEM destroy, DMA free, and clock disable. Generation data comes first from OF match and then hardware ident, with `WARN_ON` if they differ. Remove destroys sysfs/DRM/GEM, frees scratch page, powers off SMS, and disables clock.

State and persistence: Device state includes generation/revision, mapped registers, clock/reset handles, MMU scratch page, queues, perfmon info, stats, global reset counter, and DRM registration. Per-file state includes scheduler entities, stats, and perfmons.

Dependencies and integration points: Integrates platform/OF, DRM render ioctls/syncobj/GEM, GPU scheduler, V3D BO/MMU/IRQ/perfmon/sysfs/scheduler/submit modules, DMA API, clocks, reset controls, and debugfs/fdinfo.

Risks and test signals: Risks include probe unwind ordering, single-core assumption, hardware/DT generation mismatch, reset fallback bridge mapping, missing IRQ cleanup on remove, and DRM_AUTH requirements. Tests should cover supported compatible strings, open/close, get-param capabilities, fdinfo, probe failures, and module unload after active jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h

Purpose: Central V3D internal header defining core device/file/BO/job/fence/perfmon/stat structures, register access macros, queue enums helpers, wait helpers, and cross-module prototypes.

Important APIs/types/functions: Defines `V3D_MAX_QUEUES`, `v3d_queue_to_string()`, `struct v3d_stats`, `v3d_queue_state`, `v3d_perfmon`, generation enum, IRQ enum, `struct v3d_dev`, `v3d_file_priv`, `v3d_bo`, `v3d_fence`, base job and specialized bin/render/TFU/CSD/CPU jobs, query metadata, submit extension state, `wait_for()` helper, `nsecs_to_jiffies_timeout()`, and prototypes for all V3D modules.

Control flow: Other compilation units share these definitions to coordinate scheduler jobs, IRQ signaling, MMU mapping, perfmon activation, BO lifetime, reset, and ioctls.

State and persistence: Describes nearly all V3D runtime state: register mappings, page table, scratch page, DRM MM, work item, queues, active jobs, locks, stats, perfmons, and global reset counter.

Dependencies and integration points: Includes DRM GEM shmem, DRM scheduler, Linux locks/workqueue, performance counter descriptors, and V3D UAPI.

Risks and test signals: Struct layout and locking contracts are high blast-radius. Risks include queue enum mismatch, timeout overflow, stale prototypes, and active-job lifetime bugs. Test signals are full-driver build, lockdep under job submission/reset, fdinfo stats, and KASAN/KCSAN during open/close/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c

Purpose: Creates V3D dma_fence objects and supplies fence driver/timeline names.

Important APIs/types/functions: `v3d_fence_create()` allocates `struct v3d_fence`, assigns device, queue, monotonically increasing queue seqno, and calls `dma_fence_init()` with queue lock/context. `v3d_fence_ops` implements `get_driver_name` and `get_timeline_name`.

Control flow: Submit paths create IRQ fences per hardware queue; IRQ handling signals them when work completes.

State and persistence: Fence state is per allocation: seqno, queue, device pointer, and embedded `dma_fence`. Queue state holds `emit_seqno` and `fence_context`.

Dependencies and integration points: Integrates Linux dma-fence and V3D queue state. Timeline names are used by debugging/synchronization tooling.

Risks and test signals: The CPU/cache-clean queues are not named in `get_timeline_name()` and may return NULL if used directly. Tests should validate seqno monotonicity, fence signaling, timeline names for all submitted queues, and cleanup on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c

Purpose: Initializes and destroys V3D GEM/MMU/scheduler state, performs hardware reset and cache maintenance, configures page table base, hugepage support, and invariant core state.

Important APIs/types/functions: `v3d_init_core()` and `v3d_init_hw_state()` program invariant core cache/TMU state. Reset helpers idle AXI/GCA/SMS, use reset control or bridge reset, reinitialize hardware, page table, IRQs, and perfmon state. Cache helpers invalidate/clean L3/L2/slice caches with `cache_clean_lock`. `v3d_huge_mnt_init()` configures transparent hugepage support. `v3d_gem_init()` allocates queue stats/fence contexts, initializes locks and DRM MM, allocates a 4 MiB page table, initializes hardware/MMU, hugepages, and scheduler. `v3d_gem_destroy()` tears down scheduler, stats, DRM MM, and page table.

Control flow: Probe calls `v3d_gem_init()` after scratch-page allocation. Reset is called on GPU hang and disables IRQs before hardware reset and re-enables via `v3d_irq_reset()`. Destroy runs after DRM unregister and expects no active jobs.

State and persistence: State includes queue stats, fence contexts, locks, DRM MM address space, page table DMA memory, hardware cache/MMU registers, and optional hugepage mount.

Dependencies and integration points: Integrates V3D registers, reset controls/bridge regs, IRQ, MMU, scheduler, perfmon, DRM MM, DMA coherent allocation, transparent hugepage GEM support, and tracepoints.

Risks and test signals: Risks include reset races, cache-clean/invalidate interference, 4 MiB contiguous page-table allocation failure, active jobs at destroy, and generation-specific reset/SMS behavior. Tests should cover init/destroy, GPU hang reset, CSD cache clean, THP on/off, and allocation failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c

Purpose: Handles V3D core and hub interrupts, signals job fences, services binner out-of-memory by allocating overflow memory, logs MMU/GMP faults, and manages IRQ setup/enable/disable/reset.

Important APIs/types/functions: `V3D_CORE_IRQS()` and `V3D_HUB_IRQS()` compute generation-dependent masks. `v3d_overflow_mem_work()` creates a 256 KiB BO and attaches it to the active bin/render job. `v3d_irq_signal_fence()` updates stats, clears active job, and signals IRQ fence. `v3d_irq()` handles OUTOMEM, bin/render/CSD completion, GMP violations, and shared-line fallback. `v3d_hub_irq()` handles TFU completion and MMU fault reporting. `v3d_irq_init()`, `v3d_irq_enable()`, `v3d_irq_disable()`, and `v3d_irq_reset()` manage interrupt lifecycle.

Control flow: Probe clears pending interrupts, requests either separate core/hub IRQs or one shared IRQ, then enables masks. Completion IRQs acknowledge registers first, signal active job fences, and return handled. OUTOMEM schedules work because BO allocation cannot run in interrupt context.

State and persistence: State includes IRQ numbers, single-line flag, active queue jobs, overflow work item, and temporary overflow BOs linked to render-job cleanup lists.

Dependencies and integration points: Integrates platform IRQs, DRM logging, V3D BO/MMU, scheduler stats, tracepoints, and generation-specific register maps.

Risks and test signals: Risks include NULL active jobs on spurious completion IRQs, races between overflow work and job completion, MMU fault recovery only logging, and IRQ mask mistakes. Tests should cover separate/shared IRQ configurations, bin/render/TFU/CSD completions, OOM overflow path, reset disable synchronization, and fault logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c

Purpose: Manages V3D's single-level GPU page table: MMU/TLB flush, page-table base setup, PTE insertion for BO scatterlists, and PTE removal.

Important APIs/types/functions: PTE flag constants include valid, writable, bigpage, and superpage bits. `v3d_mmu_flush_all()` flushes MMUC and clears MMU TLB with waits. `v3d_mmu_set_page_table()` writes page-table base, enables invalid/write/cap abort+interrupt behavior, configures illegal-address scratch page, enables MMUC, and flushes. `v3d_mmu_insert_ptes()` walks BO SG DMA entries, emits 4K/64K/1M PTEs when aligned, and flushes. `v3d_mmu_remove_ptes()` zeros BO PTEs and flushes.

Control flow: GEM init sets the page table once; BO creation inserts PTEs after DRM MM range allocation; BO free removes them before range release. Each insert/remove globally flushes the MMU.

State and persistence: State is the device-wide page-table DMA allocation, scratch page, and hardware MMU registers. No per-process address spaces are used.

Dependencies and integration points: Integrates DRM GEM shmem SG tables, V3D BO offsets from DRM MM, DMA addresses, V3D register macros, and wait helpers.

Risks and test signals: The design shares one address space and notes GMP client isolation is not implemented. Risks include PTE alignment mistakes, DMA address width BUG_ON, global flush timeouts, and stale mappings. Tests should cover 4K/64K/1M mappings, scatterlist boundaries, removal, MMU fault IRQs, and BO churn under workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c

Purpose: Defines V3D performance counter metadata and implements performance-monitor lifetime, start/stop capture, per-file xarray management, and perfmon ioctls including global perfmon selection.

Important APIs/types/functions: Static counter descriptor arrays cover V3D 4.2 and 7.1 events. `v3d_perfmon_init()` selects descriptors by generation. `v3d_perfmon_start()` programs counter source muxes, enables/clears counters, and records `active_perfmon`. `v3d_perfmon_stop()` optionally accumulates counter values and disables counters. Create/destroy/get-values/get-counter/set-global ioctls validate inputs, manage refcounts, copy values/descriptors, and update `global_perfmon`.

Control flow: File open initializes the perfmon xarray; close deletes all perfmons. Job submission can attach/start a perfmon; completion or get-values stops/captures. Global perfmon uses atomic exchange/compare-exchange style updates.

State and persistence: Per-file state is an xarray of `v3d_perfmon` objects with refcount, lock, counters, and accumulated values. Device state tracks active and global perfmon. Values persist only for the object lifetime.

Dependencies and integration points: Integrates V3D performance counter registers, UAPI ioctl structs, xarray, user copy, mutex/refcount helpers, and job submission/perfmon attachment outside this file.

Risks and test signals: Risks include leaked references in `set_global` clear/error paths, active/global perfmon races, generation counter-index validation, and no counter reset except object recreation. Tests should cover invalid counters, create/destroy while active, get-values capture, global set/clear/busy, concurrent files, and V3D generations without perfmon support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_perfmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h

Purpose: Defines metadata structures for V3D performance counter descriptions and generation-selected counter tables.

Important APIs/types/functions: `struct v3d_perf_counter_desc` stores category, name, and description strings. `struct v3d_perfmon_info` stores `max_counters` and a pointer to the active descriptor array.

Control flow: `v3d_perfmon_init()` fills `v3d_perfmon_info`; ioctl handlers use it for validation and descriptor copyout.

State and persistence: The structures are embedded in device state or static arrays; no standalone persistence.

Dependencies and integration points: Included by `v3d_drv.h` and used by `v3d_perfmon.c`.

Risks and test signals: Fixed string sizes define UAPI copy limits. Tests should verify descriptor truncation behavior, counter count selection, and compile-time struct availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_performance_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h

Purpose: Defines V3D register offsets, bitfields, and field helper macros for hub, GCA, bridge reset, TFU, MMU, core control, interrupts, command-list engine, performance counters, GMP, CSD, error status, and SMS registers.

Important APIs/types/functions: `V3D_MASK`, `V3D_SET_FIELD`, `V3D_SET_FIELD_VER`, and `V3D_GET_FIELD` compose/extract fields with WARN checks. Register constants are generation-aware where layouts differ, for example TFU offsets, CSD fields, performance counter mux widths, GMP offsets, and SMS state.

Control flow: All V3D implementation files use these constants through `V3D_READ/WRITE` macros from `v3d_drv.h` to program hardware, decode identities/faults, reset blocks, manage caches, submit work, and read perf counters.

State and persistence: No state; it encodes hardware ABI.

Dependencies and integration points: Depends on Linux bit operations and is central to V3D BO/MMU/IRQ/GEM/debugfs/perfmon/submit code.

Risks and test signals: Incorrect constants cause hardware faults. A notable risk is that register definitions are broad and generation-gated by callers, so misuse can compile cleanly. Test signals include register dump sanity on each supported generation, get-param values, MMU fault decoding, perf counter programming, CSD submits, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_regs.h -->
