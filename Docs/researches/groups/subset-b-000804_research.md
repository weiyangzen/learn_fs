# subset-b-000804 research

Grouped research for PS3 platform support and pseries platform support files under the ceph-client PowerPC source tree. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/repository.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/repository.c

Purpose: Provides the PS3 LV1 repository access layer. It encodes repository node names, reads PS3 platform inventory and partition metadata, locates devices/resources, exposes storage, memory, SPU, boot-data, VUART, BE, clock, and LPM privilege information, and optionally writes/deletes highmem region nodes.

Important APIs/types/functions: Defines PS3 vendor/LPAR constants and helpers `make_first_field()`, `make_field()`, and `read_node()`. Public readers include bus/device functions, `ps3_repository_find_device()`, `ps3_repository_find_device_by_id()`, `ps3_repository_find_devices()`, `ps3_repository_find_bus()`, `ps3_repository_find_interrupt()`, `ps3_repository_find_reg()`, storage-region readers, memory readers, SPU reservation readers, boot-data/VUART readers, BE/timebase readers, and `ps3_repository_read_lpm_privileges()`. Under `CONFIG_PS3_REPOSITORY_WRITE`, highmem write/delete helpers wrap LV1 create/write/delete calls.

Control flow: All normal reads flow through `read_node()`, which resolves the current LPAR id when requested, calls `lv1_read_repository_node()`, converts LV1 failure into `-ENOENT`, and copies up to two 64-bit values to callers. Higher-level helpers build fixed node paths such as `bus/dev/reg/data`, iterate bounded bus/device/resource indexes, and stop on not-found conditions. Compound readers call lower-level readers in sequence and return the first error.

State and persistence: The file keeps no global mutable runtime cache; repository contents live in the PS3 hypervisor. The write path persists highmem metadata into repository nodes when enabled. Temporary state is stack-local `ps3_repository_device` snapshots and read values. Debug dumping is compiled only under `DEBUG`.

Dependencies and integration points: Depends on `asm/lv1call.h`, `platform.h`, PS3 repository naming conventions, PS3 system bus discovery, memory setup, SPU setup, storage drivers, VUART/system-manager setup, and time calibration. It is an integration boundary between Linux platform code and LV1 repository services.

Risks: Hard-coded search bounds of 10 buses/devices/resources can miss firmware layouts outside assumptions. Many readers assign output values even when the read failed, so callers must honor return codes. Node-field encoding depends on endian/layout details of copied strings. Optional write support can leave partially updated highmem metadata if only one of the base/size writes or deletes succeeds.

Test signals: Useful signals include PS3 boot logs with repository reads, successful discovery of storage/network/USB/GPU/VUART devices, SPU resource enumeration, timebase calibration from BE data, highmem region import/export, `DEBUG` repository dumps, and fault-injection of LV1 `NO_ENTRY` paths.

Source read size: 1380 lines, 32930 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/repository.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/setup.c

Purpose: Defines the PS3 machine setup and lifecycle hooks. It initializes firmware version state, SPU/SMP hooks, early memory and hash page table setup, preallocated PS3 framebuffer/flash buffers, firmware sysfs reporting, power management, restart/poweroff/halt/panic behavior, and kexec CPU teardown.

Important APIs/types/functions: Exports `ps3_gpu_mutex`, `ps3_get_firmware_version()`, `ps3_compare_firmware_version()`, `ps3fb_videomemory`, and `ps3flash_bounce_buffer`. Key local functions are `ps3_power_save()`, `ps3_restart()`, `ps3_power_off()`, `ps3_halt()`, `ps3_panic()`, `prealloc()`, early params `ps3fb` and `ps3flash`, `ps3_set_dabr()`, `ps3_setup_sysfs()`, `ps3_setup_arch()`, `ps3_early_mm_init()`, `ps3_probe()`, and `ps3_kexec_cpu_down()`.

Control flow: `define_machine(ps3)` binds platform callbacks. Probe saves OS-area parameters and installs `pm_power_off`; setup reads LV1 version info, formats `fw-version`, installs SPU and SMP support, preallocates optional buffers, sets `ppc_md.power_save`, and initializes the OS area. Early MM setup initializes PS3 memory, VAS, and HPTE state. Shutdown paths stop secondary CPUs and call PS3 system manager operations that do not return.

State and persistence: Persistent state includes the exported GPU mutex, firmware version union/string, preallocation descriptors whose addresses are assigned through memblock, and machine callback table entries. Sysfs exposes firmware version under the firmware kobject. Panic loops in LV1 pause after flushing kernel messages.

Dependencies and integration points: Integrates with LV1 calls, PS3 OS-area code, PS3 MM/HPTE setup, PS3 IRQ code, PS3 SPU code, SMP setup, framebuffer and flash drivers, firmware sysfs, PowerPC `ppc_md`, and kexec hooks.

Risks: The preallocation sizes are parsed very early and consume memblock memory permanently. `ps3_set_dabr()` silently masks unsupported DABRX bits. Lifecycle hooks assume system-manager calls never return. Kexec teardown must clean per-CPU IPIs and IRQ state without racing with remaining CPUs.

Test signals: PS3 boot to userspace, `/sys/firmware/ps3/fw-version`, framebuffer/flash module load using preallocated buffers, DABR/debug watchpoint tests, panic/restart/poweroff behavior, SMP boot, and kexec/crash shutdown are primary signals.

Source read size: 302 lines, 6737 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/smp.c

Purpose: Implements PS3 SMP message passing by mapping PowerPC IPI message classes onto PS3 event receive ports and registering them with generic SMP IPI handling.

Important APIs/types/functions: Defines per-CPU `ps3_ipi_virqs[MSG_COUNT]`, `ps3_smp_message_pass()`, `ps3_smp_probe()`, `ps3_smp_cleanup_cpu()`, `ps3_smp_ops`, and `smp_init_ps3()`.

Control flow: Initialization installs `ps3_smp_ops`. During SMP probe, CPUs 0 and 1 get four event receive ports matching `PPC_MSG_CALL_FUNCTION`, `PPC_MSG_RESCHEDULE`, `PPC_MSG_TICK_BROADCAST`, and `PPC_MSG_NMI_IPI`; successful ports are requested as message IPIs, registered with PS3 IRQ code, and the NMI IPI is registered for debug break. Message sending looks up the target CPU/message virq and calls `ps3_send_event_locally()`. Cleanup destroys each per-CPU event receive port.

State and persistence: Persistent state is the per-CPU virq array. There is no dynamic allocation in this file beyond event ports created by helper APIs. Cleanup resets each virq slot to zero.

Dependencies and integration points: Depends on PS3 event-port helpers, generic PowerPC SMP message numbers, `smp_request_message_ipi()`, PS3 IRQ registration, debug break IPI support, and machine setup calling `smp_init_ps3()`.

Risks: The code assumes exactly two CPUs and fixed message-number ordering, enforced only by `BUILD_BUG_ON()`. Failed event setup leaves some message virqs zero; later sends to those messages may fail in lower layers. Cleanup cannot call `free_irq()` and relies on event-port destruction being sufficient.

Test signals: PS3 SMP boot, reschedule and call-function IPI traffic, tick broadcast, debug/NMI IPI, CPU shutdown/kexec cleanup, and logs for failed event receive port setup are relevant.

Source read size: 120 lines, 2540 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/spu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/spu.c

Purpose: Provides PS3-specific Cell SPU management and priv1 operations. It constructs logical SPEs through LV1, maps SPU regions, wires SPU interrupts, enumerates SPU resource reservations, and installs platform hooks consumed by the generic SPU/spufs code.

Important APIs/types/functions: Defines `enum spe_type`, `struct spe_shadow`, `enum spe_ex_state`, `struct priv1_cache`, and `struct spu_pdata`. Public `ps3_get_spe_id()` and `ps3_spu_set_platform()` bridge external users. Core helpers include `get_vas_id()`, `construct_spu()`, `setup_areas()`, `setup_interrupts()`, `enable_spu()`, `ps3_create_spu()`, `ps3_destroy_spu()`, `ps3_enumerate_spus()`, and `spu_priv1_ps3_ops`.

Control flow: `ps3_spu_set_platform()` installs management and priv1 ops. Enumeration reads repository SPU resource ids and calls the generic SPU creation callback for exclusive resources. Creation allocates `spu_pdata`, records the resource id, constructs a logical SPE, enables it, maps shadow/local-store/problem/priv2 areas, sets up three interrupt classes, and spins until the shadow execution status reports executed. Destruction disables the SPE, tears down interrupts and mappings, destructs the logical SPE, and frees private data.

State and persistence: Persistent per-SPU state lives in `spu->pdata`: LV1 SPE id, resource id, LV1 area addresses, ioremapped shadow pointer, cached interrupt masks, SR1, and TCLASS id. Shadow registers are read-only mappings of hypervisor-provided SPE state. Interrupt masks and selected priv1 registers are cached because reads are not all directly available from LV1.

Dependencies and integration points: Depends on LV1 SPE calls, PS3 repository resource reservations, PS3 SPE IRQ setup, generic `struct spu`, `spu_management_ops`, `spu_priv1_ops`, spufs, and Cell SPU register definitions.

Risks: `ps3_create_spu()` busy-waits without timeout for executed state. Failure cleanup after allocation calls `ps3_destroy_spu()`, which contains `BUG_ON()` calls and assumes enough fields were initialized. Priv1 mask read-modify-write comments question caller serialization. `mfc_sr1_set()` enforces hypervisor-allowed bits with `BUG_ON()`.

Test signals: SPU enumeration count, spufs mount and SPU context execution, SPU interrupt delivery for all classes, SPU enable/disable paths, priv1 register behavior under workloads, and error injection for LV1 construct/enable/map failures are useful.

Source read size: 620 lines, 14680 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/spu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/system-bus.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/system-bus.c

Purpose: Implements the PS3 platform bus, LV1 device open/close wrappers, MMIO region mapping, DMA mapping operations, device registration, driver registration, uevents, and device-driver matching for PS3 system devices.

Important APIs/types/functions: Exports `ps3_open_hv_device()`, `ps3_close_hv_device()`, `ps3_mmio_region_create()`, `ps3_free_mmio_region()`, `ps3_mmio_region_init()`, `ps3_system_bus_device_register()`, `ps3_system_bus_driver_register()`, and `ps3_system_bus_driver_unregister()`. Key structures include the root `ps3_system_bus`, `usage_hack`, `ps3_system_bus_type`, MMIO ops, and DMA ops for SB and IOC0 devices.

Control flow: Core init registers the root device and bus when PS3 LV1 firmware is present. Drivers match devices by `match_id` and optional `match_sub_id`; probe/remove/shutdown delegate to `ps3_system_bus_driver` callbacks. Device registration assigns parent, bus, release callback, DMA ops, and generated names by device type. Open/close route storage/network/USB devices through `lv1_open_device()/lv1_close_device()` and GPU/sound through `lv1_gpu_open()/lv1_gpu_close()`, with reference counters for shared devices.

State and persistence: Persistent state includes bus registration, the fake root device, static device counters for naming, DMA operation tables, and `usage_hack` counters protected by a mutex. MMIO regions remember bus address, length, page size, and returned LPAR address. DMA mappings persist in PS3 DMA regions external to this file until unmapped.

Dependencies and integration points: Integrates with Linux driver core, DMA API, PS3 LV1 device/MMIO/GPU calls, PS3 DMA region helpers, PS3 device descriptors from repository enumeration, module autoload through `MODALIAS=ps3:id:subid`, and system shutdown.

Risks: The `usage_hack` is an explicit FIXME rather than a general reference model and only covers selected devices. Several default or unexpected cases call `BUG()`. Scatter-gather and IOC0 operations are incomplete or assert in some configurations. DMA mapping returns may not consistently use `DMA_MAPPING_ERROR` on `ps3_dma_map()` failure.

Test signals: Driver binding and modalias autoload for PS3 devices, LV1 open/close balance under multiple clients, MMIO create/free, DMA coherent/map/unmap tests for SB and IOC0, shutdown callbacks, and hot error paths for failed LV1 calls are relevant.

Source read size: 807 lines, 19473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/system-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/time.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/time.c

Purpose: Provides PS3 timebase calibration, boot-time retrieval, and RTC platform-device registration.

Important APIs/types/functions: Implements `ps3_calibrate_decr()`, local `read_rtc()`, `ps3_get_boot_time()`, and device init `ps3_rtc_init()`.

Control flow: Decrementer calibration reads BE timebase frequency from the repository for BE index 0, stores it in `ppc_tb_freq`, and derives `ppc_proc_freq` as 40 times the timebase. Boot time reads LV1 RTC and adds PS3 OS-area RTC offset. Device init registers a simple `rtc-ps3` platform device only when PS3 LV1 firmware is present.

State and persistence: The file updates global PowerPC clock-frequency variables and relies on persistent OS-area RTC diff state. It holds no local mutable global state.

Dependencies and integration points: Depends on PS3 repository BE clock data, LV1 `lv1_get_rtc()`, PS3 OS-area helpers, PowerPC time setup, and the `rtc-ps3` driver.

Risks: Calibration and RTC reads use `BUG_ON()` on firmware errors, so bad repository/RTC data is fatal. The processor-frequency multiplier is PS3-specific. RTC platform-device creation has no resources and assumes the driver knows how to call platform helpers.

Test signals: Correct boot-time wall clock, stable decrementer/timer behavior, visible `rtc-ps3` platform device, RTC driver probe, and PS3 boot with repository BE clock data are useful.

Source read size: 59 lines, 1051 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Kconfig

Purpose: Defines pseries platform build-time feature selection for IBM PowerVM/PAPR systems, including LPAR, shared-processor accounting, event IRQs, LPAR config, shared memory/CMM, HTM dump, hypervisor counters, IBM VIO/eBus, SVM, PAPR SCM, and keystore features.

Important APIs/types/functions: Major symbols are `PPC_PSERIES`, `PARAVIRT`, `PARAVIRT_SPINLOCKS`, `PARAVIRT_TIME_ACCOUNTING`, `PPC_SPLPAR`, `DTL`, `PSERIES_ENERGY`, `IO_EVENT_IRQ`, `LPARCFG`, `PPC_PSERIES_DEBUG`, `PPC_SMLPAR`, `CMM`, `HTMDUMP`, `HV_PERF_CTRS`, `VPA_PMU`, `IBMVIO`, `IBMEBUS`, `PSERIES_PLPKS`, `PAPR_SCM`, and `PPC_SVM`.

Control flow: Kconfig has no runtime flow; it establishes dependency and `select` relationships. Enabling `PPC_PSERIES` pulls in RTAS, XICS/XIVE, MSI, dynamic OF, hotplug CPU, SWIOTLB, and other architecture infrastructure. Optional entries gate compilation of the source files in this subset through the Makefile.

State and persistence: State is build configuration. Defaults such as `PPC_PSERIES=y`, `PPC_SPLPAR=y`, `IO_EVENT_IRQ=y`, `CMM=y`, `HTMDUMP=m`, and `HV_PERF_CTRS=y` influence the generated kernel image and modules.

Dependencies and integration points: This file integrates pseries platform code with architecture-wide config symbols such as `PPC64`, `PPC_BOOK3S`, `DEBUG_FS`, `MEMORY_HOTPLUG`, `LIBNVDIMM`, `ARCH_HAS_CC_PLATFORM`, and `KVM_BOOK3S_64_HV`.

Risks: Heavy `select` usage can enable large subsystem surfaces implicitly. Feature defaults compile pseries functionality into many PPC64 builds. Incorrect dependencies can produce link failures or runtime code on unsupported firmware.

Test signals: Config-matrix builds for pseries with and without debugfs, hotplug, CMM, HTM, secure guest, IBM eBus, and PAPR SCM; `scripts/config` dependency checks; and boot smoke tests on PowerVM LPARs are the main signals.

Source read size: 217 lines, 6753 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Makefile

Purpose: Maps pseries Kconfig symbols to object files and applies pseries debug compile flags and sanitizer exclusions.

Important APIs/types/functions: Always-built objects include core pseries LPAR, RTAS, setup, firmware, DLPAR, PCI, EEH, mobility, RNG, platform attributes, and DTL code. Conditional objects include SMP, kexec, energy, CPU/memory hotplug, hypervisor console/server, hcall instrumentation, CMM, HTM dump, IO event IRQs, LPAR config, VIO, IBM eBus, PAPR SCM, VPHN, SVM, fadump, PLPKS, suspend, and VAS.

Control flow: The Makefile has no runtime flow. Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` to decide built-in versus module compilation. `ccflags-$(CONFIG_PPC_PSERIES_DEBUG)` adds `-DDEBUG`; KASAN is disabled for real-mode sensitive `ras.o` and `kexec.o`.

State and persistence: Build output composition is the persistent effect. Objects selected here define which machine initcalls and exported symbols are present in the kernel/module set.

Dependencies and integration points: Integrates the pseries directory with the architecture Kbuild system and Kconfig symbols from `Kconfig`. It is the direct build linkage for the pseries files in this subset.

Risks: Object ordering in `obj-y` can matter for initcall/link ordering and symbol availability. Moving a file between built-in and modular form can change exported symbol requirements. Real-mode code must stay out of sanitizer instrumentation.

Test signals: PPC64 pseries allyesconfig/allmodconfig/defconfig builds, module load tests for optional objects, and link checks when toggling each `CONFIG_*` symbol are useful.

Source read size: 43 lines, 1573 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cc_platform.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cc_platform.c

Purpose: Implements pseries confidential-computing capability queries for the generic Linux `cc_platform_has()` interface.

Important APIs/types/functions: Exports `cc_platform_has(enum cc_attr attr)`. It currently recognizes `CC_ATTR_MEM_ENCRYPT` and returns `is_secure_guest()`.

Control flow: A simple switch returns true for memory encryption only when the pseries secure guest/SVM helper reports protected execution. Unknown attributes return false.

State and persistence: No local state is stored. The answer is derived from architecture secure-guest state.

Dependencies and integration points: Depends on `linux/cc_platform.h`, `asm/svm.h`, and the `ARCH_HAS_CC_PLATFORM`/`PPC_SVM` configuration path. Generic DMA, memory encryption, and confidential-computing code can query this exported function.

Risks: The implementation is intentionally narrow; new attributes will silently return false until added. Incorrect `is_secure_guest()` state would affect memory encryption and DMA policy decisions.

Test signals: Secure guest boot tests, generic `cc_platform_has(CC_ATTR_MEM_ENCRYPT)` consumers, non-secure LPAR checks, and config builds with `ARCH_HAS_CC_PLATFORM` are relevant.

Source read size: 26 lines, 496 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cc_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cmm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cmm.c

Purpose: Implements IBM pseries Collaborative Memory Management, a ballooning driver that loans pages to the hypervisor and reclaims them based on PowerVM memory pressure requests.

Important APIs/types/functions: Defines module parameters `delay`, `hotplug_delay`, `oom_kb`, `min_mem_mb`, `debug`, `simulate`, and `disable`; globals `loaned_pages`, `loaned_pages_target`, `oom_freed_pages`, `hotplug_mutex`, `cmm_thread_ptr`, and `b_dev_info`; helpers `plpar_page_set_loaned()`, `plpar_page_set_active()`, `cmm_alloc_pages()`, `cmm_free_pages()`, `cmm_get_mpp()`, `cmm_thread()`, OOM/reboot/memory notifiers, sysfs registration, optional `cmm_migratepage()`, and module init/exit.

Control flow: Init checks CMO firmware support or simulation mode, registers notifiers and sysfs, initializes balloon metadata, and starts `cmmthread` unless disabled. The thread sleeps, pauses after memory hotplug, calls `h_get_mpp()` or simulation state, computes a target respecting minimum memory and OOM freed pages, then loans or frees balloon pages. OOM notification frees a configured amount of loaned pages. Disable stops the thread and frees all loaned pages.

State and persistence: Persistent kernel state includes the balloon page list, atomic loaned count, target count, OOM freed count, hotplug occurrence flag, sysfs device files, module parameters, and the CMM kthread. Loaned state also persists in hypervisor page state via `H_PAGE_INIT`.

Dependencies and integration points: Integrates with PowerVM hcalls, CMO page size, Linux balloon subsystem, OOM notifier, reboot notifier, memory hotplug notifier, sysfs bus/device registration, and optional balloon migration.

Risks: Hypervisor page-state transitions must be rolled back correctly on partial failure. Hotplug and balloon activity share delicate locking. OOM and disable paths can change the target while the thread is active. Simulation exposes extra sysfs control. Failure after sysfs registration must unwind all notifiers and devices.

Test signals: CMO-enabled LPAR ballooning, sysfs `loaned_kb`/`loaned_target_kb`/`oom_freed_kb`, OOM-triggered reclaim, memory hotplug suspend/resume behavior, reboot returning all pages active, balloon migration, simulation mode, and module unload are key signals.

Source read size: 631 lines, 15741 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dlpar.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dlpar.c

Purpose: Provides common Dynamic Logical Partitioning support for pseries CPU, memory, persistent memory, and device-tree hotplug. It parses RTAS configure-connector output, applies dynamic OF changesets, acquires/releases DRCs, dispatches hotplug error logs, and exposes a sysfs control entry.

Important APIs/types/functions: Defines `struct pseries_hp_work`, `struct cc_workarea`, property/node parsing helpers, `dlpar_configure_connector()`, `dlpar_attach_node()`, `dlpar_detach_node()`, `dlpar_acquire_drc()`, `dlpar_release_drc()`, `dlpar_unisolate_drc()`, DRC lookup helpers, `handle_dlpar_errorlog()`, `queue_hotplug_event()`, command parsers, `dlpar_workqueue_init()`, and the `/sys/kernel/dlpar` attribute.

Control flow: `dlpar_configure_connector()` repeatedly calls RTAS `ibm,configure-connector`, interpreting return codes as node, sibling, child, property, parent, complete, or error operations. DRC acquire/release validates entity state and sets allocation/isolation indicators. Hotplug error logs dispatch to memory, CPU, PMEM, or device-tree handlers. Sysfs commands parse `<resource> <action> <id_type> <id>` into the same error-log shape. Queued firmware events run through an ordered workqueue.

State and persistence: Persistent state is the ordered workqueue and sysfs attribute. Dynamic OF nodes/properties allocated from configure-connector are either attached to the live tree or freed. DRC allocation/isolation state persists in firmware.

Dependencies and integration points: Depends on RTAS tokens, RTAS work areas, dynamic Open Firmware changesets, pseries hotplug resource handlers, kernel hotplug locking, and kernel object sysfs.

Risks: Configure-connector parsing is stateful and can leak or corrupt a node tree if sibling/parent sequencing is unexpected. Rollback must free unattached dynamic nodes but not live tree nodes. Sysfs parser rejects PMEM even though dispatcher handles it. DRC state changes require correct rollback on subsequent attach/online failure.

Test signals: Manual `/sys/kernel/dlpar` add/remove for memory, CPU, and device-tree resources, firmware hotplug event queueing, configure-connector failure injection, OF changeset validation, DRC acquire/release traces, and hotplug rollback tests are useful.

Source read size: 827 lines, 16792 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dlpar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dtl.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dtl.c

Purpose: Implements pseries Dispatch Trace Log support and stolen-time accounting integration for shared-processor LPARs. It can expose per-CPU DTL buffers through debugfs and scan dispatch entries for virtual CPU accounting.

Important APIs/types/functions: Defines `struct dtl`, optional `struct dtl_ring`, per-CPU `cpu_dtl` and `dtl_rings`, `dtl_event_mask`, `dtl_buf_entries`, `consume_dtle()`, `dtl_start()`, `dtl_stop()`, `dtl_current_index()`, `dtl_enable()`, `dtl_disable()`, debugfs file ops, `dtl_init()`, `scan_dispatch_log()`, `pseries_accumulate_stolen_time()`, and `pseries_calculate_stolen_time()`.

Control flow: Debugfs init creates `/sys/kernel/debug/powerpc/dtl` files for each possible CPU on SPLPAR systems. Opening a CPU file allocates a per-CPU buffer, registers it with the hypervisor or hooks native accounting consumption, and enables event logging. Reads copy whole `struct dtl_entry` records from the ring while handling wrap and overflow. Accounting scans PACA dispatch logs with interrupts disabled and subtracts stolen time from user/system accounting buckets.

State and persistence: Per-CPU state includes buffer pointer, CPU id, buffer entries, last read index, and lock. Native accounting mode adds per-CPU ring state and a global consumer pointer protected by atomic count. LPPACA `dtl_enable_mask`, `dtl_idx`, PACA `dtl_ridx`, and `dtl_curr` are persistent runtime accounting state.

Dependencies and integration points: Depends on SPLPAR firmware feature, LPPACA/PACA layout, `register_dtl()`/`unregister_dtl()`, `dtl_cache` and `dtl_access_lock`, debugfs, virtual CPU accounting, and PowerPC time accounting.

Risks: Only one reader is allowed per CPU, and conflicts with other DTL users must be enforced by `dtl_access_lock`. Ring overflow drops old entries. Barriers are required to publish entries and write indexes in the right order. Accounting must run with interrupts disabled and avoid tracing recursion.

Test signals: Debugfs DTL open/read/close, buffer wrap tests, SPLPAR stolen-time accounting under CPU contention, native and non-native accounting configs, lockdep around `dtl_access_lock`, and overflow behavior are important.

Source read size: 444 lines, 9717 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/eeh_pseries.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/eeh_pseries.c

Purpose: Implements pseries platform operations for Enhanced Error Handling of PCI devices and PEs using RTAS. It discovers PE config addresses, enables EEH, queries/reset PEs, retrieves error logs, configures bridges, supports SR-IOV allow-unfreeze, and registers pseries EEH ops.

Important APIs/types/functions: Maintains RTAS tokens for EEH functions, `slot_errbuf`, `slot_errbuf_lock`, and `eeh_error_buf_size`. Key functions include `pseries_pcibios_bus_add_device()`, `pseries_eeh_get_pe_config_addr()`, `pseries_eeh_phb_reset()`, `pseries_eeh_phb_configure_bridge()`, PCI capability scanners, `pseries_eeh_init_edev()`, `pseries_eeh_probe()`, exported `pseries_eeh_init_edev_recursive()`, EEH ops callbacks, SR-IOV allow-unfreeze helpers, and `eeh_pseries_init()`.

Control flow: Init resolves required RTAS tokens, selects `ibm,configure-pe` or `ibm,configure-bridge`, sets EEH flags, optionally resets PHBs for kdump/reset, and calls `eeh_init()`. Device add initializes the `eeh_dev`, discovers PE address via `ibm,get-config-addr-info*`, enables EEH using `ibm,set-eeh-option`, inserts the device into the PE tree, and saves BARs. Runtime EEH core callbacks issue RTAS state, reset, log, bridge configure, and config-space operations.

State and persistence: Persistent state includes RTAS token ids, EEH flags, PE tree relationships, per-device capability offsets/mode bits, PE config addresses, saved BAR state, SR-IOV last allow-unfreeze return codes, and the static RTAS-accessible error buffer.

Dependencies and integration points: Integrates with PCI device nodes, `pci_dn`, EEH core, RTAS PCI config access, pseries PCI hotplug, crashdump/reset flows, SR-IOV, proc/log error handling, and `ppc_md.pcibios_bus_add_device`.

Risks: PE address discovery differs across firmware revisions. Error-log buffer access uses a global spinlock because RTAS writes to a shared buffer. Reset/configure delays must match firmware semantics. VF PE insertion is manually adjusted after initial tree placement. Missing RTAS token support disables all EEH.

Test signals: PCI EEH probe logs, injected MMIO errors, PE freeze/thaw/reset recovery, bridge reconfiguration, RTAS error-log capture, SR-IOV VF recovery and allow-unfreeze, kdump/reset PHB reset path, and PCI hotplug/DLPAR device add are key.

Source read size: 926 lines, 25323 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/eeh_pseries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/event_sources.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/event_sources.c

Purpose: Provides a small helper to request all interrupts described by a pseries `/event-sources` device-tree node.

Important APIs/types/functions: Implements `request_event_sources_irqs(struct device_node *np, irq_handler_t handler, const char *name)`.

Control flow: Iterates interrupt indexes 0 through 15, calls `of_irq_get()`, stops when no more IRQs are described, warns and continues on zero virq, and requests each valid IRQ with the supplied handler and name. Any `request_irq()` failure warns and stops.

State and persistence: No local state. Persistent effects are requested IRQ handlers owned by the interrupt subsystem.

Dependencies and integration points: Used by pseries event-source clients such as IO event IRQ setup. Depends on OF IRQ translation and Linux IRQ request APIs.

Risks: The helper has a hard limit of 16 IRQs and does not unwind already requested IRQs if a later request fails. It passes `NULL` as dev_id, so handlers/freeing must be compatible with that ownership model.

Test signals: Event-source node IRQ enumeration, IO event interrupt initialization, warning paths for bad OF IRQs, and interrupt delivery to registered handlers are relevant.

Source read size: 30 lines, 676 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/event_sources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/firmware.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/firmware.c

Purpose: Probes early pseries firmware capabilities from flat device-tree properties and sets `powerpc_firmware_features` bits for hypervisor calls and architecture vector features.

Important APIs/types/functions: Defines `struct hypertas_fw_feature`, `hypertas_fw_features_table`, `fw_hypertas_feature_init()`, `struct vec5_fw_feature`, `vec5_fw_features_table`, `fw_vec5_feature_init()`, `probe_fw_features()`, and `pseries_probe_fw_features()`.

Control flow: Early flat-DT scan visits depth-1 `rtas` and `chosen` nodes. The RTAS path reads `ibm,hypertas-functions`, marks LPAR, and matches NUL-separated hcall names, with optional wildcard suffix matching, to feature bits. The chosen path reads `ibm,architecture-vec-5` and maps option-vector bits to firmware features. Secure guests disable `FW_FEATURE_PUT_TCE_IND` after hypertas parsing.

State and persistence: Persistent state is the global firmware feature bitmask. The feature tables are `__initdata`, and static flags in `probe_fw_features()` terminate scanning once both relevant nodes are seen.

Dependencies and integration points: Depends on early flat device tree APIs, firmware feature flags, option-vector macros, pseries setup, and secure guest detection. Many pseries subsystems gate behavior on the bits set here.

Risks: Matching is string-table based and sensitive to firmware naming. Wildcard matching only supports trailing `*`. Secure guest feature masking must stay aligned with DMA/TCE security constraints. Missing early properties can disable downstream functionality.

Test signals: Early boot feature logs, `/proc/cpuinfo` or debug exposure of firmware features, LPAR/SPLPAR/VIO/PLPKS/PAPR SCM feature-dependent drivers probing, secure guest boot confirming TCE-indirect disable, and flat-DT unit tests are useful.

Source read size: 191 lines, 5222 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-cpu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-cpu.c

Purpose: Implements pseries CPU hotplug and DLPAR CPU add/remove. It manages RTAS CPU stop, logical CPU id assignment, present/online maps, OF node attach/detach, DRC state, NUMA/cache metadata, and optional CPU probe/release callbacks.

Important APIs/types/functions: Key state includes `rtas_stop_self_token` and per-node `node_recorded_ids_map`. Important functions include `pseries_cpu_offline_self()`, `pseries_cpu_disable()`, `pseries_cpu_die()`, `find_cpu_id_range()`, `pseries_add_processor()`, `pseries_remove_processor()`, `dlpar_offline_cpu()`, `dlpar_online_cpu()`, DRC index validation, `dlpar_cpu_add()`, `pseries_cpuhp_detach_nodes()`, `dlpar_cpu_remove()`, `dlpar_cpu()`, OF reconfig notifier, `pseries_cpu_hotplug_init()`, and `pseries_dlpar_init()`.

Control flow: Boot init checks RTAS stop/query tokens and installs SMP CPU hotplug callbacks. DLPAR add validates the requested CPU DRC under `/cpus`, acquires the DRC, configures connector nodes, attaches nodes with an OF changeset, updates NUMA distance, and onlines all allowed threads. Remove offlines all threads, releases the DRC, detaches the CPU node and uniquely referenced cache nodes, and rolls back by reacquiring/onlining if detach fails. OF reconfig events update `cpu_present_mask` and hard CPU ids.

State and persistence: Persistent state includes CPU online/present masks, hard SMP processor ids, PACA `cpu_start`, boot CPU id, per-node recorded id masks, NUMA lookup tables, dynamic OF CPU/cache nodes, DRC allocation/isolation state, and installed `smp_ops` callbacks.

Dependencies and integration points: Depends on RTAS stop-self and query stopped state, XICS/XIVE teardown and IRQ migration, VPA/SLB shadow unregister, CPU device hotplug core, topology SMT policy, dynamic OF notifiers, pseries DLPAR common helpers, and NUMA topology update functions.

Risks: Logical CPU ids must preserve SMT sibling adjacency while avoiding cross-node id reuse. Removing the last online CPU is blocked but races are guarded by CPU hotplug locks. Rollback after partial add/remove must restore DRC and online state. Cache node detachment depends on accurate use counts across CPUs and cache hierarchy.

Test signals: CPU DLPAR add/remove by DRC index, SMT-disabled online policy, last-CPU removal rejection, XICS and XIVE interrupt migration, NUMA id assignment across nodes, OF reconfig notifier behavior, kexec/offline stop-self path, and rollback injection are primary.

Source read size: 904 lines, 20202 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-memory.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-memory.c

Purpose: Implements pseries memory hotplug and DLPAR memory add/remove for dynamic reconfiguration memory. It updates LMB associativity, adds/removes Linux memory blocks, onlines/offlines memory devices, updates DRMEM state, and handles OF reconfiguration.

Important APIs/types/functions: Defines property clone/free helpers, `find_aa_index()`, `update_lmb_associativity_index()`, `lmb_to_memblock()`, `get_lmb_range()`, `dlpar_change_lmb_state()`, hot-remove helpers under `CONFIG_MEMORY_HOTREMOVE`, `dlpar_add_lmb()`, `dlpar_memory_add_by_count/index/ic()`, `dlpar_memory_remove_by_count/index/ic()`, `dlpar_memory()`, `pseries_add_mem_node()`, memory OF notifier, and `pseries_memory_hotplug_init()`.

Control flow: Add paths validate target LMBs, acquire DRCs, configure connector data to derive associativity, update lookup arrays when needed, call `__add_memory()`, online memory blocks, mark LMBs assigned, and roll back added LMBs if a count/range add is incomplete. Remove paths validate removability, offline memory blocks, call `__remove_memory()`, update memblock and associativity, clear assignment, release DRCs, and roll back removed LMBs on partial failure. Successful DLPAR operations refresh the DRMEM device-tree property.

State and persistence: Persistent state includes `drmem_info` LMB flags, DRC state, LMB associativity indexes, `/ibm,dynamic-reconfiguration-memory` properties, Linux memory block online/offline state, memblock regions, NUMA distance data, and dynamic OF memory node changes.

Dependencies and integration points: Depends on pseries DLPAR common helpers, DRMEM infrastructure, memory hotplug core, memblock, NUMA associativity lookup arrays, fadump reservations, dynamic OF reconfig notifiers, and firmware LMB/DRC conventions.

Risks: Partial add/remove rollback is complex and must not leak DRCs or leave LMB flags inconsistent. Fadump and reserved LMBs must not be removed. Associativity lookup array updates allocate and replace OF properties dynamically. `pseries_remove_memblock()` updates `base` during removal before `memblock_remove()`, which is a sensitive path to audit.

Test signals: Memory DLPAR add/remove by count, index, and indexed-count; rollback injection; DRMEM property refresh; NUMA associativity changes; fadump reserved-memory protection; memory block online/offline sysfs state; and builds without `CONFIG_MEMORY_HOTREMOVE` are key.

Source read size: 929 lines, 20632 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/htmdump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/htmdump.c

Purpose: Implements a debugfs interface for PowerVM Hardware Trace Macro data and control through the `H_HTM` hcall.

Important APIs/types/functions: Maintains global buffers and selectors `nodeindex`, `nodalchipindex`, `coreindexonchip`, `htmtype`, `htmconfigure`, `htmstart`, `htmsetup`, and `htmflags`. Key functions include `htm_return_check()`, read handlers for trace/status/info/caps/system memory, setters/getters for configure/start/setup/flags, `htmdump_init_debugfs()`, module init, and module exit.

Control flow: Module init refuses to run inside KVM guests, allocates page buffers, and creates `arch_debugfs_dir/htmdump` controls. Reads issue `H_HTM` dump/status/capability/config hcalls using current selector globals and copy returned buffer data to userspace. Write controls configure/deconfigure, start/stop, set up buffer size, and choose wrap mode, updating local state only on successful hcall completion.

State and persistence: Persistent state consists of debugfs files, allocated page buffers, selector/control globals, and HTM hypervisor state changed by configure/start/setup hcalls. No locking protects concurrent debugfs readers/writers.

Dependencies and integration points: Depends on debugfs, PowerVM `htm_hcall_wrapper()`, hcall return codes, `arch_debugfs_dir`, physical-address access to kmalloc buffers, and KVM guest detection.

Risks: Global buffers and controls are shared across all users without serialization. Error unwinding in `htmdump_init_debugfs()` can leak earlier buffers if a later allocation fails before module exit. Several readers trust output-buffer header fields for copy sizes. `htmdump_read()` updates `*ppos` but passes a local offset to `simple_read_from_buffer()`, making repeated-read semantics worth testing.

Test signals: Debugfs file creation, capability/status/info reads on HTM-capable PowerVM, configure/start/stop/setup/flags writes, hcall error-code mapping, concurrent debugfs access, module unload leak checks, and KVM guest refusal are useful.

Source read size: 589 lines, 15960 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/htmdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall.S

Purpose: Provides low-level pseries hypervisor call wrappers in assembly for no-return-buffer, 4-return, 9-return, raw real-mode-capable, and tracepoint-instrumented hcalls.

Important APIs/types/functions: Defines `plpar_hcall_norets_notrace`, `plpar_hcall_norets`, `plpar_hcall`, `plpar_hcall_raw`, `plpar_hcall9`, and `plpar_hcall9_raw`. Trace support uses `HCALL_INST_PRECALL`, `HCALL_INST_POSTCALL_NORETS`, `HCALL_INST_POSTCALL`, `HCALL_BRANCH`, `hcall_tracepoint_refcount`, and static branch/jump-label integration.

Control flow: Each wrapper saves condition register state, arranges arguments into the ABI registers expected by `HVSC`, invokes the hypervisor, stores return registers into the caller-supplied buffer where applicable, clears `PACASRR_VALID`, restores condition register state, and returns the hcall status in r3. Trace variants snapshot arguments, call `__trace_hcall_entry`, perform the hcall, store returns, call `__trace_hcall_exit`, and restore LR/stack.

State and persistence: The assembly mutates caller return buffers, PACA SRR-valid state, tracepoint refcount/static branch state, and volatile registers according to the PowerPC ABI. Raw variants intentionally avoid per-CPU/stat memory so they can be used in real mode.

Dependencies and integration points: Depends on PowerPC assembly ABI, `HVSC`, PACA offsets, stack parameter offsets, tracepoint C hooks, jump labels, feature fixups, and many pseries callers using `plpar_*` wrappers.

Risks: Register save/restore and stack layout are correctness-critical. Trace instrumentation must preserve all hcall arguments and return values. Raw wrappers must remain safe for real-mode kexec/kdump contexts. Clearing `PACASRR_VALID` must happen after every hypervisor call path.

Test signals: Hcall-heavy boot, tracepoint enable/disable, hcall return-buffer correctness for 4- and 9-return calls, kdump/kexec raw hcalls in real mode, objdump review after asm-offset changes, and lockdep/tracing recursion checks are relevant.

Source read size: 370 lines, 6975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall_inst.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall_inst.c

Purpose: Implements debugfs hcall instrumentation by recording per-CPU, per-hcall counts and time totals from hcall tracepoints.

Important APIs/types/functions: Defines `struct hcall_stats`, per-CPU `hcall_stats[HCALL_STAT_ARRAY_SIZE]`, seq_file operations, trace probes `probe_hcall_entry()` and `probe_hcall_exit()`, and init `hcall_inst_init()`.

Control flow: Init on LPAR registers hcall entry/exit trace probes and creates debugfs directory `hcall_inst` with one file per possible CPU. Entry probe records timebase and PURR start for the opcode slot. Exit probe increments call count and accumulates elapsed timebase and PURR. Seq output skips zero-count hcalls and prints opcode, calls, TB total, and optionally PURR total.

State and persistence: Persistent state is per-CPU stats arrays. Probe start fields are overwritten on each hcall entry per opcode and CPU. Debugfs files reference the per-CPU arrays directly.

Dependencies and integration points: Depends on hcall tracepoints emitted by `hvCall.S`, debugfs, seq_file, firmware LPAR feature detection, timebase, PURR CPU feature, and pseries machine initcalls.

Risks: Nested or reentrant hcalls with the same opcode on one CPU would overwrite start timestamps. No debugfs reset operation is provided. Trace registration failure must unwind entry probe registration. PURR reads depend on CPU feature availability for display but are still accumulated.

Test signals: Enabling `CONFIG_HCALL_STATS`, debugfs `hcall_inst/cpuN` contents after hcall activity, tracepoint registration failure tests, CPU hotplug visibility, and comparison against ftrace hcall events are useful.

Source read size: 140 lines, 3297 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall_inst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvconsole.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvconsole.c

Purpose: Provides low-level PowerVM LPAR virtual terminal character I/O helpers for hvc console drivers.

Important APIs/types/functions: Exports `hvc_get_chars()` and `hvc_put_chars()`.

Control flow: `hvc_get_chars()` issues `H_GET_TERM_CHAR`, copies two returned big-endian 64-bit words into the caller buffer, and returns the firmware byte count on success or zero otherwise. `hvc_put_chars()` clamps count to firmware maximum, sends up to 16 bytes through `H_PUT_TERM_CHAR`, and maps `H_SUCCESS`, `H_BUSY`, and other errors to count, `-EAGAIN`, or `-EIO`.

State and persistence: No local state is retained. Data movement is through caller buffers and hcall return registers.

Dependencies and integration points: Depends on `plpar_hcall()`/`plpar_hcall_norets()`, hvc console core, PowerVM virtual terminal hcalls, and endian conversion of 16-byte payload chunks.

Risks: Callers must supply a buffer large enough for two unsigned long words even when requesting fewer bytes. Failed get operations discard error detail by returning zero. The helpers assume hcall payload alignment compatible with casting `u8 *` to `unsigned long *`.

Test signals: HVC console input/output on pseries LPAR, busy retry behavior, max-count clamping, unaligned buffer audits, and console stress during boot/panic are relevant.

Source read size: 75 lines, 1941 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvconsole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvcserver.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvcserver.c

Purpose: Provides architecture-specific API helpers for IBM hypervisor virtual console server adapters, including partner discovery and connection registration/freeing.

Important APIs/types/functions: Defines `hvcs_convert()`, exported `hvcs_free_partner_info()`, helper `hvcs_next_partner()`, exported `hvcs_get_partner_info()`, `hvcs_register_connection()`, and `hvcs_free_connection()`.

Control flow: Partner discovery initializes the caller-supplied page buffer, iteratively calls `H_VTERM_PARTNER_INFO` using the previous partner id/address as cursor, stops on all-ones terminator, allocates `struct hvcs_partner_info` entries with `GFP_ATOMIC`, copies location code text, and appends to the caller list. Connection helpers issue `H_REGISTER_VTERM` and `H_FREE_VTERM`, mapping hypervisor return codes to Linux errnos.

State and persistence: The file owns no global mutable state. Persistent effects are caller-owned partner info lists and hypervisor vterm connection state. Allocated list entries must be freed through `hvcs_free_partner_info()`.

Dependencies and integration points: Depends on PowerVM hcalls, `struct hvcs_partner_info`, hvcs driver code, page-sized firmware work buffer supplied by caller, and list management.

Risks: Partner discovery may be called under spinlock, so allocations use `GFP_ATOMIC` and can fail. If firmware returns an error after some partners, the function treats partial lists as success. Connection `-EINVAL` has ambiguous firmware meaning and may require caller refresh/retry. `more` is constant but loop exits through terminator or error.

Test signals: HVCS partner enumeration, connection open/close, busy retry on free, partial partner-list behavior, allocation failure cleanup, and module user stress under concurrent console changes are useful.

Source read size: 239 lines, 7296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvcserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ibmebus.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ibmebus.c

Purpose: Implements the IBM eBus platform bus for GX-bus based pseries adapters, with simple DMA ops, OF device creation, driver registration wrappers, IRQ mapping helpers, sysfs probe/remove controls, and bus/device attributes.

Important APIs/types/functions: Defines fake parent `ibmebus_bus_device`, exported `ibmebus_bus_type`, default matches for `IBM,lhca` and `IBM,lhea`, DMA ops, `ibmebus_create_device()`, `ibmebus_create_devices()`, exported `ibmebus_register_driver()`/`ibmebus_unregister_driver()`, exported IRQ helpers, sysfs `probe`/`remove`, bus match/probe/remove/shutdown callbacks, device attributes, and `ibmebus_bus_init()`.

Control flow: Postcore init registers the bus and fake parent, then creates devices for default OF matches. Driver registration creates any matching devices not already on the bus before registering the platform driver on `ibmebus`. Sysfs `probe` creates a device from an OF path if not already present; `remove` unregisters a matching platform device. Bus probe calls the platform driver's probe after OF match and holds an extra device reference until remove.

State and persistence: Persistent state includes registered bus, fake parent device, platform devices on the bus, sysfs attributes, and driver bindings. DMA operations map coherent memory and physical/scatterlist addresses as direct virtual addresses, reflecting the eBus platform model.

Dependencies and integration points: Depends on OF platform device allocation, Linux driver core, IRQ domain mapping, platform drivers for IBM GX adapters, and pseries machine postcore init.

Risks: DMA ops are nonstandard direct virtual mappings and only support a 64-bit mask. Manual sysfs probe/remove must handle invalid paths and duplicate devices. Probe path `get_device()` must be balanced by remove; driver probe failures drop the reference. IRQ helpers use a NULL irqdomain mapping and assume firmware interrupt specifiers are globally resolvable.

Test signals: eBus init on big-endian pseries, auto-created LHEA/LHCA devices, manual sysfs probe/remove, driver bind/unbind, IRQ request/free, DMA map_sg/coherent behavior, and OF modalias uevents are relevant.

Source read size: 480 lines, 11482 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ibmebus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/io_event_irq.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/io_event_irq.c

Purpose: Implements pseries RTAS IO event interrupt handling and exposes an atomic notifier chain for device drivers that consume IO event sections.

Important APIs/types/functions: Exports `ATOMIC_NOTIFIER_HEAD(pseries_ioei_notifier_list)`, stores `ioei_check_exception_token`, uses RTAS buffer `ioei_rtas_buf`, and defines `ioei_find_event()`, `ioei_interrupt()`, and `ioei_init()`.

Control flow: Init resolves RTAS `check-exception`, finds `/event-sources/ibm,io-events`, and requests all event-source IRQs using `request_event_sources_irqs()`. On interrupt, the handler loops calling `check-exception` for the IRQ hardware number and RTAS IO events until RTAS returns nonzero. Each returned error log is validated as IO type, the IO event section is extracted, and the notifier chain is called so clients can claim or ignore the event.

State and persistence: Persistent state includes the notifier chain, RTAS token, cacheline-aligned shared RTAS buffer, and registered IRQ handlers. Event ownership is external to this file and determined by notifier clients.

Dependencies and integration points: Depends on RTAS error-log parsing, event-source IRQ helper, OF event-source node, IRQ hardware number translation, and `asm/io_event_irq.h` clients.

Risks: A single global RTAS buffer is used in interrupt context; concurrent IO event IRQs could contend if firmware routes more than one. Events must be processed sequentially and in returned order. Missing or malformed IO event sections are warned once and skipped. Notifier clients must be atomic-context safe.

Test signals: IO event interrupt initialization, RTAS check-exception loops with multiple events, notifier client registration/claiming, malformed event-log warning paths, interrupt storm handling, and absence of IO event node/token are useful.

Source read size: 161 lines, 5017 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/io_event_irq.c -->
