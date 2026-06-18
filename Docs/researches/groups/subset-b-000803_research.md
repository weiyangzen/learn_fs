# subset-b-000803 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/rng.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/rng.c

### Purpose
`rng.c` wires PowerNV random-number sources into `ppc_md.get_random_seed`, preferring POWER9 DARN and falling back to device-tree `ibm,power-rng` MMIO engines.

### Important APIs, Types, And Functions
`struct pnv_rng` holds virtual and real-mode MMIO addresses plus a whitening mask. Key functions are `initialise_darn()`, `pnv_get_random_darn()`, exported `pnv_get_random_long()`, `rng_create()`, `pnv_get_random_long_early()`, `pnv_rng_init()`, and `pnv_rng_late_init()`.

### Control Flow
Early platform setup calls `pnv_rng_init()`. DARN is tested up to ten times on ARCH_300 CPUs and installed if usable. Otherwise, an early lazy callback waits until slab allocation works, creates `pnv_rng` objects for `ibm,power-rng` nodes, maps registers, assigns each CPU to the same-chip RNG where possible, and replaces the callback with `pnv_get_random_long()`. The late init path forces lazy setup if needed and publishes OF platform devices.

### State, Persistence, And Dependencies
State is per-CPU RNG pointer assignment plus the mutable per-device whitening mask. Reads use normal MMIO when translation is on and real-mode reads when MSR_DR is off. Dependencies include OF address parsing, chip-id topology, `asm/archrandom.h`, DARN opcodes, and PowerNV machine init calls.

### Integration Points
The file feeds architecture random seed consumers through `ppc_md.get_random_seed` and exports `pnv_get_random_long()` for GPL users.

### Risks
The fallback assumes every CPU gets a non-NULL RNG pointer before use. The whitening mask is updated without locking and may be shared by CPUs on the same chip. DARN error handling must reject the all-ones failure value.

### Test Signals
Boot logs on POWER8/POWER9, `ibm,power-rng` DT coverage, early and late random seed calls, real-mode callers, and repeated DARN failure injection are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/setup.c

### Purpose
`setup.c` defines the PowerNV machine descriptor and the platform lifecycle: firmware feature discovery, security mitigation setup, SMP/interrupt startup, reboot/poweroff, kexec teardown, transactional memory enablement, and CPU info reporting.

### Important APIs, Types, And Functions
Important functions include `pnv_setup_security_mitigations()`, `pnv_setup_arch()`, `pnv_init()`, `pnv_init_IRQ()`, `pnv_restart()`, `pnv_power_off()`, `pnv_shutdown()`, `pnv_kexec_cpu_down()`, `pnv_setup_machdep_opal()`, `pnv_probe()`, `pnv_tm_init()`, `pnv_get_proc_freq()`, and `define_machine(powernv)`.

### Control Flow
`pnv_probe()` detects OPAL firmware, installs OPAL machdep callbacks, and performs early platform init. `setup_arch` then configures speculation mitigations from `/ibm,opal/fw-features`, initializes SMP, NVRAM, NAP power save, guarded-core warnings, and RNG. IRQ init prefers native XIVE and falls back to XICS. Shutdown paths stop OPAL events, stop secondary CPUs, disable interrupts, and loop in OPAL reboot/poweroff calls until completion or fallback.

### State, Persistence, And Dependencies
State is mostly global architecture callback state: `ppc_md`, `pm_power_off`, security feature flags, `powersave_nap`, CPU feature bits, hardware description strings, PACA MCE buffers, and kexec state. Dependencies include OPAL, XIVE/XICS, PCI, memblock, CPU feature tables, transactional memory flags, and security mitigation helpers.

### Integration Points
The machine descriptor plugs this code into generic PowerPC boot, `/proc/cpuinfo`, PCI discovery, machine shutdown, memory hotplug block sizing, kexec CPU teardown, and early machine-check recovery.

### Risks
Mitigation policy depends on exact firmware feature names and default-on/default-off semantics. Reboot and poweroff loops can spin forever if OPAL never completes. Kexec teardown must put CPUs and interrupt controllers into a state the next kernel can use.

### Test Signals
PowerNV boot on hash/radix systems, `/proc/cpuinfo`, OPAL reboot modes (`full`, `fast`, `mpipl`, `error`), kexec/kdump, XIVE/XICS fallback, firmware-feature DT variants, and TM enabling on POWER9 are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/smp.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/smp.c

### Purpose
`smp.c` implements PowerNV SMP operations: starting CPUs through OPAL, CPU hotplug/offline loops, IPI routing through doorbells or interrupt controllers, NMI IPI delivery, and registration of PowerNV `smp_ops`.

### Important APIs, Types, And Functions
Key functions are `pnv_smp_setup_cpu()`, `pnv_smp_kick_cpu()`, hotplug helpers `pnv_smp_cpu_disable()`, `pnv_cpu_offline_self()`, `pnv_flush_interrupts()`, `pnv_cpu_bootable()`, `pnv_smp_probe()`, `pnv_cause_ipi()`, `pnv_system_reset_exception()`, `pnv_cause_nmi_ipi()`, and `pnv_smp_init()`.

### Control Flow
Secondary start asks OPAL about the hardware CPU state, starts inactive threads at `generic_secondary_smp_init`, and then kicks the PACA path. Per-CPU setup enables a POWER9 HMI workaround and configures XIVE or XICS. Hotplug marks the CPU offline, migrates interrupt state, enters a loop with hard IRQs disabled, naps through `pnv_cpu_offline()`, handles wake reasons, and exits when restart is requested or crash IPIs arrive. Probe patches `smp_ops->cause_ipi` to doorbell implementations when supported.

### State, Persistence, And Dependencies
State lives in `smp_ops`, PACA fields, `boot_cpuid`, systemcfg processor counts, interrupt-controller state, and CPU online/dead masks. Dependencies include OPAL CPU status/start calls, XIVE/XICS, doorbells, cpuidle, KVM host IPI state, kdump, and subcore split checks.

### Integration Points
The file is called from PowerNV setup and generic CPU hotplug/SMP code. NMI IPI support plugs into `ppc_md.system_reset_exception`.

### Risks
CPU state races with OPAL, kexec, and hotplug can strand CPUs. Offline loops must clear wakeup interrupts correctly and preserve crash dump behavior. Doorbell fallback must remain valid on older cores.

### Test Signals
CPU online/offline stress, boot with SMT limits, kexec/kdump, XIVE and XICS systems, doorbell IPI tests, NMI IPI behavior, and POWER9 HMI setup are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore-asm.S -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore-asm.S

### Purpose
`subcore-asm.S` provides the secondary-thread real-mode helper used while splitting a POWER8 core into subcores.

### Important APIs, Types, And Functions
The exported assembly symbol is `split_core_secondary_loop(u8 *state)`. It uses sync step constants from `subcore.h` and SPRs such as HID0, LDBAR, PMMAR, PMCR, RPR, SDR1, LPID, PCR, and HDEC.

### Control Flow
The routine saves MSR, disables interrupts, transitions to real mode via SRR0/SRR1 and `rfid`, reads unsplit SPR values, stores `SYNC_STEP_REAL_MODE` to the shared state byte, spins until HID0 reports 2-way or 4-way LPAR mode, initializes per-subcore SPRs, restores saved SPR values including SDR1, and returns to virtual mode with the original MSR.

### State, Persistence, And Dependencies
State is the caller-provided byte used for synchronization and CPU SPR state preserved across the split. It depends on exact POWER8 HID0 semantics and the C side's stop-machine synchronization.

### Integration Points
`subcore.c` calls this helper from nonzero threads during `split_core()`.

### Risks
Interrupts must stay disabled so SRR0/SRR1 are not clobbered. Returning to virtual mode before SDR1 is restored would be unsafe. HID0 bit definitions and SPR save/restore order are architecture-sensitive.

### Test Signals
Successful 1-to-2 and 1-to-4 subcore transitions, no hangs in the real-mode wait loop, preserved MMU operation after split, and offline-thread participation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.c

### Purpose
`subcore.c` controls POWER8 dynamic subcore split mode and exposes `/sys/devices/system/cpu/subcores_per_core`.

### Important APIs, Types, And Functions
It maintains `subcores_per_core`, `new_split_mode`, `cpu_offline_mask`, and per-CPU `struct split_state`. Important functions are `unsplit_core()`, `split_core()`, `cpu_do_split()`, `cpu_core_split_required()`, `update_subcore_sibling_mask()`, `cpu_update_split_mode()`, `set_subcores_per_core()`, sysfs show/store handlers, and `subcore_init()`.

### Control Flow
Mode changes run under `stop_machine_cpuslocked()`. The master CPU publishes `new_split_mode`, wakes offline CPUs, and all CPUs first unsplit if needed. Nonzero threads nap for unsplit or enter the real-mode assembly loop for split; thread 0 updates HID0 and SLW state, waits for hardware mode bits, then the master updates global topology and PACA sibling masks.

### State, Persistence, And Dependencies
State persists in global split mode variables, per-CPU sync bytes, `threads_per_subcore`, and PACA sibling masks. SLW HID0 patches persist for idle/winkle wakeups. Dependencies include OPAL SLW calls, cpuidle supported-state queries, KVM HV mode checks, CPU topology helpers, and stop-machine.

### Integration Points
SMP offline loops call `cpu_core_split_required()` so offline CPUs can participate. Sysfs provides runtime control, and `subcore_init()` installs the attribute only on supported POWER8-family PVRs.

### Risks
All threads in a core must be present; partial CPU limits disable the feature. Split changes are rejected while KVM HV mode is active. Missing barriers or failed offline wakeups can deadlock stop-machine.

### Test Signals
Sysfs writes of `1`, `2`, and `4`, unsupported PVR no-op behavior, KVM-active rejection, CPU hotplug during split, and sibling-mask/topology validation are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.h

### Purpose
`subcore.h` defines synchronization constants and declarations shared by the C and assembly subcore split implementation.

### Important APIs, Types, And Functions
The ordered constants are `SYNC_STEP_INITIAL`, `SYNC_STEP_UNSPLIT`, `SYNC_STEP_REAL_MODE`, and `SYNC_STEP_FINISHED`. Under SMP it declares `split_core_secondary_loop()` and `update_subcore_sibling_mask()`; non-SMP gets an empty inline for sibling-mask updates.

### Control Flow
The constants are compared with `<=`/`<` style waits in `subcore.c` and are written directly by the assembly helper.

### State, Persistence, And Dependencies
The header has no storage of its own. It depends on being included consistently by C and assembler and on the constant ordering remaining monotonic.

### Integration Points
It bridges `subcore.c` and `subcore-asm.S`.

### Risks
Changing numeric order would break synchronization waits. Missing declarations under config combinations would break builds.

### Test Signals
SMP and non-SMP compile coverage plus split-mode runtime tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ultravisor.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ultravisor.c

### Purpose
`ultravisor.c` detects IBM Ultravisor firmware and exposes its memory console through sysfs.

### Important APIs, Types, And Functions
`early_init_dt_scan_ultravisor()` sets `FW_FEATURE_ULTRAVISOR` when an `ibm,ultravisor` flat-DT node appears. `uv_init()` finds `ibm,uv-firmware`, initializes `uv_memcons`, creates `/sys/firmware/ultravisor`, and publishes a read-only `msglog` binary attribute. `uv_msglog_read()` copies from the memconsole.

### Control Flow
Early DT scanning marks the firmware feature. A PowerNV machine subsystem initcall returns immediately without the feature, otherwise locates the UV firmware node, initializes memcons, sizes the bin attribute, creates the kobject, and registers the sysfs file.

### State, Persistence, And Dependencies
State is `ultravisor_kobj`, `uv_memcons`, and the initialized bin attribute size. The exposed persistence is the firmware-backed memconsole content.

### Integration Points
This integrates with firmware feature detection, `firmware_kobj`, sysfs binary attributes, and the generic `memcons` helper.

### Risks
Missing or malformed DT nodes disable exposure. Kobject creation or sysfs file creation can fail after memcons initialization without explicit cleanup. Access permissions intentionally restrict the log to root-readable.

### Test Signals
Boot with and without Ultravisor nodes, sysfs `msglog` reads at offsets, and error paths for missing `ibm,uv-firmware` validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ultravisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-debug.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-debug.c

### Purpose
`vas-debug.c` exposes PowerNV VAS instance/window state through debugfs.

### Important APIs, Types, And Functions
Functions include `cop_to_str()`, `info_show()`, `hvwc_show()`, `print_reg()`, `vas_init_dbgdir()`, `vas_instance_init_dbgdir()`, `vas_window_init_dbgdir()`, and `vas_window_free_dbgdir()`.

### Control Flow
VAS instance creation calls `vas_instance_init_dbgdir()`, which lazily creates the root `vas` debugfs directory and then a per-instance directory. Window allocation calls `vas_window_init_dbgdir()` to create `w<id>/info` and `w<id>/hvwc`. The seq-file show callbacks lock `vas_mutex`, verify the window remains mapped, and print metadata or HV window-context registers.

### State, Persistence, And Dependencies
State is the root debugfs dentry, per-instance names/directories, and per-window debug names/directories. Output reflects live MMIO register state, not persisted software state.

### Integration Points
It depends on `vas.h` register offset macros and `read_hvwc_reg()`, and is called from VAS instance/window lifecycle code.

### Risks
Debugfs reads race window close unless `vas_mutex` is respected. A failed debugfs or name allocation silently skips observability. Register reads require mapped HVWC context.

### Test Signals
Opening and closing VAS windows, reading debugfs `info` and `hvwc`, and concurrent close/read stress are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-fault.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-fault.c

### Purpose
`vas-fault.c` handles NX/VAS translation faults for user send windows through a per-VAS fault receive window and FIFO.

### Important APIs, Types, And Functions
Important functions are threaded IRQ handler `vas_fault_thread_fn()`, hard IRQ handler `vas_fault_handler()`, fault FIFO diagnostic `dump_fifo()`, and `vas_setup_fault_window()`.

### Control Flow
Instance setup allocates a 4 MiB fault FIFO, invalidates CRB slots, initializes a `VAS_COP_TYPE_FAULT` receive window, and stores it in the instance. The IRQ handler uses `fault_lock` and `fifo_in_progress` to wake only one thread. The thread walks FIFO CRBs until it reaches an invalid entry, copies each CRB, invalidates the slot, returns fault-window credit, resolves the PSWID to a user send window, updates the user completion/status block, and returns send-window credit.

### State, Persistence, And Dependencies
State is `fault_fifo`, `fault_crbs`, `fault_fifo_size`, `fault_win`, `fifo_in_progress`, and credit registers in VAS hardware. Dependencies include CRB layout, `vas_update_csb()`, `vas_pswid_to_window()`, and VAS credit return helpers.

### Integration Points
`vas.c` requests the threaded IRQ and calls `vas_setup_fault_window()`. `vas-window.c` points user send windows at the fault window when an IRQ is available.

### Risks
Invalid PSWIDs imply lost ability to return user credits. FIFO pointer wrap and CRB invalidation must match hardware. Continuous faults rely on `fifo_in_progress` to avoid missed work.

### Test Signals
User NX-GZIP page faults, multiple CRBs per interrupt, FIFO wrap, credit restoration, bad PSWID diagnostics, and user-window close while faults are pending are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-trace.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-trace.h

### Purpose
`vas-trace.h` defines tracepoints for VAS receive-window open, send-window open, and CRB paste operations.

### Important APIs, Types, And Functions
Trace events are `vas_rx_win_open`, `vas_tx_win_open`, and `vas_paste_crb`. They record current task pid, VAS id, coprocessor type, lpid/pid/tid attributes, window id, and paste kernel address depending on the event.

### Control Flow
`vas-window.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted. Window open and paste paths call the trace hooks before validation or hardware paste.

### State, Persistence, And Dependencies
There is no retained state beyond ftrace/perf trace buffers. Dependencies include tracepoint infrastructure, `struct vas_rx_win_attr`, `struct vas_tx_win_attr`, and `struct pnv_vas_window`.

### Integration Points
The header sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so generated trace code can locate it from the PowerNV source directory.

### Risks
Trace fields must stay in sync with public VAS attribute structures. The paste event assumes a `pnv_vas_window` pointer with valid `vinst` and `paste_kaddr`.

### Test Signals
Kernel trace builds, enabling each tracepoint, and VAS open/paste workloads showing expected fields validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-window.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-window.c

### Purpose
`vas-window.c` implements PowerNV VAS window lifecycle and operations: allocating window IDs, mapping context/paste regions, programming HV/UW window registers, opening RX/TX windows, paste/copy helpers, credit handling, close sequencing, PSWID lookup, and user API registration.

### Important APIs, Types, And Functions
Public/exported functions include `vas_win_paste_addr()`, `vas_init_rx_win_attr()`, `vas_rx_win_open()`, `vas_init_tx_win_attr()`, `vas_tx_win_open()`, `vas_copy_crb()`, `vas_paste_crb()`, `vas_win_close()`, `vas_return_credit()`, `vas_pswid_to_window()`, `vas_register_api_powernv()`, and `vas_unregister_api_powernv()`. Internal helpers manage MMIO mapping, register initialization, window tables, RX references, and close polling.

### Control Flow
Window allocation reserves an ID from the instance IDA, maps HVWC/UWC MMIO bars, and creates debugfs entries. RX open validates attributes, programs context for NX, fault, or FTW receive windows, and records the window in instance lookup tables. TX open validates attributes, resolves the matching RX window, programs translation/credit/fault/PSWID registers, maps a kernel paste page for kernel windows or attaches user mm context for user windows, and records the window. Paste uses the copy/paste instruction wrapper and optional report-enable offset. Close unmaps paste, waits for not-busy and credits, clears open/pin bits, removes table entries, drops RX/user references, and frees mappings/ID.

### State, Persistence, And Dependencies
State spans `struct pnv_vas_window`, instance `windows[]`/`rxwin[]` tables, IDA allocations, hardware window context registers, paste mappings, debugfs entries, RX reference counts, task/mm references for user windows, and hardware credits. Dependencies include VAS workbook register layouts, `copy-paste.h`, MMIO, IRQ/fault support, mm context VAS helpers, and the generic `asm/vas.h` API.

### Integration Points
NX compression/GZIP and user coprocessor APIs open windows through these exports. Fault handling uses PSWID lookup and credit return. `vas.c` provides instances and IRQ ports.

### Risks
Close waits can stall indefinitely if hardware credits or busy state do not clear. Mapping errors must unwind RX references and IDs. User windows require successful fault IRQ setup. Register programming order matters because `WINCTL_OPEN` is written last.

### Test Signals
Kernel NX requests, user NX-GZIP mmap/open/close, credit exhaustion, paste success/failure return codes, fault-window paths, debugfs lifecycle, and concurrent open/close stress are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-window.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.c

### Purpose
`vas.c` discovers VAS hardware instances from device tree, allocates per-instance state, configures global fault IRQs/windows, maps CPU-to-VAS affinity, and registers the platform driver.

### Important APIs, Types, And Functions
Important symbols are global `vas_mutex`, `init_vas_instance()`, `vas_irq_fault_window_setup()`, `find_vas_instance()`, exported `chip_to_vas_id()`, `vas_probe()`, and `vas_init()`.

### Control Flow
`vas_init()` registers the platform driver and manually creates platform devices for `ibm,vas` nodes. Probe reads `ibm,vas-id`, `ibm,chip-id`, and four resources, initializes `struct vas_instance`, derives paste window shift, allocates a XIVE IRQ on the chip, maps it to a Linux virq, captures the XIVE trigger page as IRQ port, assigns CPUs on the same chip to this VAS id, links the instance globally, optionally sets up threaded fault handling and a fault window, initializes debugfs, and stores driver data.

### State, Persistence, And Dependencies
State includes the global instance list, `cpu_vas_id` per-CPU mapping, per-instance IDA/window tables/mutex/fault fields, IRQ mapping, and BAR addresses. Dependencies include OF platform resources, XIVE native IRQ allocation, IRQ domains, `vas-fault.c`, and debugfs helpers.

### Integration Points
Window open paths call `find_vas_instance()`. External users can map a chip to a VAS id with `chip_to_vas_id()`.

### Risks
Several error paths after IRQ allocation return without freeing earlier allocations. VAS expects exactly four DT resources and a sane paste shift. If fault setup fails, user send windows are disabled by clearing `virq`.

### Test Signals
DT probing with multiple chips, CPU affinity mapping, XIVE IRQ allocation failures, fault-window setup failure, and `vasid == -1` local lookup are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.h

### Purpose
`vas.h` is the private PowerNV VAS hardware definition header: register offsets/bitfields, state structures, helper enums, inline MMIO accessors, and internal function declarations.

### Important APIs, Types, And Functions
It defines window limits and context sizes, many `VAS_*_OFFSET`/bitmask macros, `VREG()`, enums for notify scope, DMA type, and notify-after-count, FIFO invalid markers, `struct vas_instance`, `struct pnv_vas_window`, `struct vas_winctx`, declarations for instance/debug/fault/window helpers, inline `vas_window_pid()`, `write_uwc_reg()`, `write_hvwc_reg()`, `read_hvwc_reg()`, `encode_pswid()`, and `decode_pswid()`.

### Control Flow
The header itself has no runtime control flow, but its accessors perform big-endian MMIO writes/reads and log nonzero register writes. PSWID helpers encode VAS id and window id for later fault lookup.

### State, Persistence, And Dependencies
The structures define all persistent VAS software state: instance resources, fault FIFO fields, window lookup tables, window mappings, paste address, RX reference counts, and register configuration snapshots. Hardware persistence is in the programmed window context registers.

### Integration Points
All PowerNV VAS implementation files include this header, and public `asm/vas.h` users indirectly depend on these private structures through exported functions.

### Risks
Incorrect bitfield definitions corrupt hardware programming. `windows[VAS_WINDOWS_PER_CHIP]` is large per instance. PSWID encoding comments and shifts must match fault decode expectations.

### Test Signals
Build coverage, register dumps matching hardware documentation, PSWID encode/decode round trips, and VAS open/fault workloads validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Kconfig

### Purpose
`Kconfig` declares the PS3 platform and related driver/configuration options.

### Important APIs, Types, And Functions
Primary symbols are `PPC_PS3`, `PS3_ADVANCED`, `PS3_HTAB_SIZE`, `PS3_DYNAMIC_DMA`, `PS3_VUART`, `PS3_PS3AV`, `PS3_SYS_MANAGER`, `PS3_VERBOSE_RESULT`, `PS3_REPOSITORY_WRITE`, `PS3_STORAGE`, `PS3_DISK`, `PS3_ROM`, `PS3_FLASH`, `PS3_VRAM`, and `PS3_LPM`.

### Control Flow
Kconfig dependencies gate PS3 on 64-bit big-endian Book3S PowerPC and select Cell, PCI, and endian-specific USB support. Advanced options reveal otherwise hidden tuning controls. Storage and AV/system manager options select common PS3 support symbols.

### State, Persistence, And Dependencies
The file contributes build-time configuration state only. Selected symbols determine compiled code in the PS3 platform, storage, AV, VUART, LPM, and DMA paths.

### Integration Points
The options affect Makefile object inclusion and driver availability across PS3 system-bus, storage, video/audio, and platform memory code.

### Risks
Dependencies are architecture-specific; accidental enablement on little-endian or non-Cell targets would be invalid. `PS3_DYNAMIC_DMA` and repository write support expose experimental or bootloader-oriented behavior.

### Test Signals
`olddefconfig`, PS3 defconfig builds, advanced option toggles, module/built-in combinations for storage and AV, and dependency visibility checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Makefile

### Purpose
The PS3 `Makefile` selects platform object files for PS3 builds.

### Important APIs, Types, And Functions
It always builds `setup.o`, `mm.o`, `time.o`, `hvcall.o`, `htab.o`, `interrupt.o`, `exports.o`, `os-area.o`, `system-bus.o`, and `device-init.o`. It conditionally builds `gelic_udbg.o`, `smp.o`, and `spu.o`.

### Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` assignments to include PS3 platform code and optional early debug, SMP, and SPU support.

### State, Persistence, And Dependencies
The file carries build graph state only. It depends on config symbols defined in PS3 Kconfig and broader PowerPC config.

### Integration Points
It ties PS3 architecture sources into the kernel image or modules selected by the architecture build.

### Risks
Missing an always-needed object breaks platform boot. Optional object guards must match declarations in `platform.h`.

### Test Signals
PS3 builds with early GELIC debug, SMP on/off, and SPU on/off validate object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/device-init.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/device-init.c

### Purpose
`device-init.c` discovers PS3 hypervisor repository devices and registers Linux PS3 system-bus, storage, VUART, graphics, sound, LPM, and ramdisk devices, including a background storage probe thread.

### Important APIs, Types, And Functions
Key setup functions cover LPM, GELIC, USB EHCI/OHCI, VUART, storage, sound, graphics, ramdisk, dynamic/static repository devices, and `ps3_register_devices()`. Notification support uses `struct ps3_notification_device`, `ps3_notification_interrupt()`, `ps3_notification_read_write()`, `ps3_probe_thread()`, and reboot notifier `ps3_stop_probe_thread()`.

### Control Flow
The device initcall exits unless `FW_FEATURE_PS3_LV1` is present, starts a storage probe kthread, registers VUART/graphics/sound/LPM/ramdisk devices, and enumerates static SB devices. Storage notifications use a pseudo storage device, an event receive port, IRQ handler, and 512-byte command/event buffer. Each notification read can lead to repository lookup by bus/dev id and dynamic storage device registration.

### State, Persistence, And Dependencies
Allocated device layouts persist after successful registration and contain DMA/MMIO regions or storage region arrays. `probe_task` persists until reboot notifier stops it. Dependencies include LV1 storage calls, repository helpers, PS3 system bus registration, DMA/MMIO region init, interrupts, rcuwait, kthreads, and freezer support.

### Integration Points
The registered devices are consumed by PS3 GELIC, USB, storage, AV, sys-manager, sound, graphics, LPM, and ramdisk drivers.

### Risks
Failure paths rely on each setup function freeing only unregistered allocations. The async notification path must avoid tag mismatches and stop cleanly on reboot. Some repository devices can be inaccessible and are intentionally ignored.

### Test Signals
Boot enumeration logs, storage hot/late readiness, IRQ notification flow, kthread freezer/reboot stop, repository failure injection, and driver binding for each match id are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/device-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/exports.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/exports.c

### Purpose
`exports.c` exports PS3 LV1 hypercall wrapper symbols to modules.

### Important APIs, Types, And Functions
It defines `LV1_CALL(name, in, out, num)` to declare `_lv1_<name>` and `EXPORT_SYMBOL()` it, then includes `<asm/lv1call.h>` to expand every LV1 call entry.

### Control Flow
There is no runtime flow; preprocessing generates export declarations for every hypercall listed in the shared LV1 call table.

### State, Persistence, And Dependencies
No state is stored. The file depends on `_lv1_*` symbols implemented by `hvcall.S` and declarations in `asm/lv1call.h`.

### Integration Points
Modules such as PS3 storage, network, AV, and debug code can call LV1 wrappers.

### Risks
Exports must stay synchronized with assembly-generated symbols. Broad exports expose low-level hypervisor operations to GPL-compatible modules.

### Test Signals
Module builds and `Module.symvers`/link checks for `_lv1_*` users validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/gelic_udbg.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/gelic_udbg.c

### Purpose
`gelic_udbg.c` implements early debug output by sending UDP broadcast packets through the PS3 GELIC network device using LV1 calls.

### Important APIs, Types, And Functions
Important functions are `map_dma_mem()`, `unmap_dma_mem()`, `gelic_debug_init()`, `gelic_debug_shutdown()`, `gelic_sendbuf()`, `ps3gelic_udbg_putc()`, exported `udbg_shutdown_ps3gelic()`, and init `udbg_init_ps3gelic()`.

### Control Flow
Initialization opens the GELIC device, maps a static debug block for DMA, builds Ethernet/VLAN/IP/UDP headers from LV1 MAC/VLAN queries, and installs `udbg_putc`. Characters accumulate until newline or a 1000-byte limit, then `gelic_sendbuf()` fills lengths/checksum, marks the descriptor card-owned, starts TX DMA, and busy-waits for completion. Shutdown unmaps DMA and closes the LV1 device.

### State, Persistence, And Dependencies
State is static DMA bus address, descriptor packet buffer, header pointers, and current message pointer. Dependencies include LV1 net control/TX DMA, raw Ethernet/IP/UDP structures, DMA mapping through LV1, and early `udbg` hooks.

### Integration Points
Selected by early debug config and used before normal console/network drivers are available.

### Risks
Errors call `lv1_panic(0)`, appropriate only for early debug. Checksums and header fields are manually built and endian-sensitive. Busy-waiting can hang if DMA never completes.

### Test Signals
Receiving UDP broadcasts on port 18194, VLAN and non-VLAN paths, shutdown cleanup, and long-line flushing validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/gelic_udbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/htab.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/htab.c

### Purpose
`htab.c` implements PS3 hash page table operations through LV1 hypervisor calls.

### Important APIs, Types, And Functions
Important functions are `ps3_hpte_insert()`, `ps3_hpte_updatepp()`, `ps3_hpte_invalidate()`, `ps3_hpte_clear()`, and `ps3_hpte_init()`. `ps3_hpte_remove()` and bolted PP update are not implemented. A spinlock serializes HTAB operations.

### Control Flow
Insert encodes HPTE V/R fields, translates physical to LPAR addresses, asks LV1 to insert into primary/secondary groups, reads back entries to determine secondary placement, and returns the Linux slot encoding. Updatepp reads the group, compares AVPN/valid bit, invalidates matching entries, and returns `-1` so the caller reinserts. Invalidate writes zero to an LV1 HTAB slot. Clear iterates every HPTE, zeros it, then shuts down PS3 memory state for kexec.

### State, Persistence, And Dependencies
State is the hypervisor HTAB and global `ppc64_pft_size`. Dependencies include hash MMU encoding helpers, LV1 HTAB calls, PS3 physical-to-LPAR translation, and PS3 memory teardown.

### Integration Points
`ps3_hpte_init()` installs the operations into `mmu_hash_ops`.

### Risks
Unimplemented remove/update-bolted paths can panic or log if used unexpectedly. Insert BUGs if all victim entries are bolted. LV1 readback is required because inserted secondary status is not otherwise known.

### Test Signals
Hash MMU boot, memory pressure, permission changes, kexec clear path, and fault tests that trigger secondary HPTE insertion validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/hvcall.S -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/hvcall.S

### Purpose
`hvcall.S` generates low-level PS3 LV1 hypercall wrapper functions that marshal input/output registers according to the shared LV1 call table.

### Important APIs, Types, And Functions
The file defines the `lv1call` instruction sequence and macro families such as `LV1_0_IN_1_OUT`, `LV1_1_IN_4_OUT`, `LV1_6_IN_3_OUT`, `LV1_7_IN_6_OUT`, and `LV1_8_IN_1_OUT`. Including `<asm/lv1call.h>` expands `_lv1_<name>` global functions.

### Control Flow
Each wrapper saves LR, may spill output pointer arguments to the caller stack frame or red-zone area, loads the LV1 API number into r11, executes the hypervisor call opcode, sign-extends the return code in r3, restores the stack, writes output registers r4+ into caller-provided pointers, restores LR, and returns.

### State, Persistence, And Dependencies
There is no persistent state; the wrappers obey the PPC64 ABI stack and register convention. Dependencies include the exact LV1 call ABI, `STACK_FRAME_MIN_SIZE`, `LRSAVE`, and the LV1 call manifest.

### Integration Points
All PS3 platform C code calls `_lv1_*` wrappers directly or through inline macros, and `exports.c` exports the same symbols for modules.

### Risks
Any macro with the wrong input/output arity corrupts stack slots or output pointers. The 6+ argument variants rely on correct stack parameter offsets. Return sign extension must match LV1 negative error codes.

### Test Signals
Assembly build, objdump inspection of representative wrappers, boot-time LV1 calls, module link tests, and runtime hypercall error propagation validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/hvcall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/interrupt.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/interrupt.c

### Purpose
`interrupt.c` implements PS3 interrupt routing between LV1 hypervisor outlets/plugs and Linux IRQs, including event receive ports, system-bus interrupts, IO IRQs, VUART IRQs, SPE IRQs, IPIs, and irqdomain setup.

### Important APIs, Types, And Functions
Key data structures are per-CPU `struct ps3_private` and `struct ps3_bmp`. Important functions include chip callbacks `ps3_chip_mask()`, `ps3_chip_unmask()`, `ps3_chip_eoi()`, setup/teardown helpers for plugs, event ports, SB events, IO, VUART, SPE, IPI registration, `ps3_get_irq()`, `ps3_init_IRQ()`, and `ps3_shutdown_IRQ()`.

### Control Flow
Init creates a no-map irqdomain, configures each CPU's LV1 interrupt state bitmap, and installs `ppc_md.get_irq`. IRQ setup constructs or receives an LV1 outlet, creates a Linux virq equal to the outlet mapping, stores per-CPU chip data, masks it, and connects the outlet to an LV1 plug. `ps3_get_irq()` intersects status and mask bitmaps, prioritizes debug-break IPIs, finds the leading set plug, EOIs IPIs immediately, and returns the plug as the IRQ.

### State, Persistence, And Dependencies
Per-CPU state includes HV status/mask bitmaps, locks, PPE/thread IDs, and IPI masks. LV1 persists outlet/plug/event-port bindings. Dependencies include irqdomain, fast EOI IRQ handling, LV1 interrupt calls, PS3 LPAR address translation, and SMP hard-thread IDs.

### Integration Points
PS3 system-bus, storage notifications, VUART, SPE, and generic interrupt handling use these exported helpers.

### Risks
Only plug values up to 63 are usable by this bitmap simplification. Mask bit polarity is HV-specific. Some destroy paths must avoid operations from interrupt context during kexec. Missing bitmap deconfiguration can leave LV1 writing stale memory.

### Test Signals
Device IRQ delivery, event-port setup/destroy, VUART IRQs, IPIs/debug breaks, CPU shutdown/kexec, and bitmap debug dumps are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/mm.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/mm.c

### Purpose
`mm.c` manages PS3 LV1 virtual address spaces, high memory regions, physical-to-LPAR translation, and PS3 DMA/IOMMU region mapping for system-bus and IOC0 devices.

### Important APIs, Types, And Functions
Core types are `struct map`, `struct mem_region`, and `struct dma_chunk`. Important APIs are exported `ps3_mm_phys_to_lpar()`, `ps3_mm_vas_create()`, `ps3_mm_vas_destroy()`, `ps3_mm_init()`, `ps3_mm_shutdown()`, `ps3_dma_region_init()`, `ps3_dma_region_create()`, `ps3_dma_region_free()`, `ps3_dma_map()`, and `ps3_dma_unmap()`. Internal ops implement SB dynamic/linear DMA and IOC0 IOPTE mappings.

### Control Flow
Early memory init reads repository RAM info, restores or allocates one highmem LV1 region, records it in the repository when enabled, adjusts total memory, and adds highmem to memblock. VAS creation queries LV1 address region capabilities, constructs/selects a virtual address space with configured HTAB size and large page support, and returns the HTAB size. DMA init chooses operation tables by device type and config. Dynamic SB DMA allocates LV1 DMA regions and maps chunks on demand; linear SB maps RAM up front; IOC0 allocates IO segments and writes IOPTEs per page.

### State, Persistence, And Dependencies
Global `map` persists real memory, high memory, VAS id, and HTAB size. DMA regions persist bus address, page size, chunk lists, locks, and device references. Dependencies include LV1 memory/VAS/DMA/IOPTE calls, repository highmem helpers, memblock, Cell IOPTE flags, and Linux DMA mask APIs.

### Integration Points
HTAB code uses `ps3_mm_phys_to_lpar()` and memory teardown. Device registration initializes DMA regions for system-bus and IOC0 devices, and PS3 drivers use map/unmap wrappers.

### Risks
The implementation assumes one highmem region and real memory base zero. Dynamic DMA chunk overlap logic BUGs on multi-chunk overlaps. IOC0 mapping has FIXME comments around length limits and reuse. Kexec teardown runs with MMU off and calls panic on LV1 cleanup failures.

### Test Signals
Boot memory map, highmem repository restore/create, kexec/kdump cleanup, SB and IOC0 DMA map/unmap stress, dynamic vs linear DMA configs, and large-page boundary cases validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/os-area.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/os-area.c

### Purpose
`os-area.c` reads, preserves, exposes, and updates PS3 flash "Other OS" area parameters such as RTC offset and AV output preference.

### Important APIs, Types, And Functions
Important structures are `os_area_header`, `os_area_params`, `os_area_db`, `db_index`, and `db_iterator`. Public APIs include `ps3_os_area_flash_register()`, `ps3_os_area_save_params()`, `ps3_os_area_init()`, `ps3_os_area_get_rtc_diff()`, `ps3_os_area_set_rtc_diff()`, and `ps3_os_area_get_av_multi_out()`. Internal helpers verify headers/DB, iterate/set/delete 64-bit DB entries, update flash, and update device-tree properties.

### Control Flow
Early save reads the boot data mirror location from the repository, verifies the header, reads params and DB, chooses RTC diff from DB, params, or default 1970-to-2000 offset, stores AV preference, marks the copy valid, and clears the header mirror. Init later restores values from the device tree for second-stage kernels if needed, writes properties to `/`, and ensures an RTC default. Setting RTC diff updates saved state and schedules work; the work updates the DT property and rewrites/formats the flash DB through registered flash ops.

### State, Persistence, And Dependencies
State persists in static `saved_params`, root DT properties `linux,rtc_diff` and `linux,av_multi_out`, and flash DB contents. Flash access is mediated by registered `ps3_os_area_flash_ops` under a mutex.

### Integration Points
PS3 time code consumes RTC diff, video code consumes AV multi-out, flash driver registers read/write ops, and second-stage kernels get values through the device tree.

### Risks
Flash updates are asynchronous and can fail after DT state changes. DB layout uses bitfields and fixed offsets. Header verification failure is expected on second-stage kernels but must not erase saved defaults.

### Test Signals
First-stage and kexec boots, valid/invalid DB formatting, RTC set from interrupt context, flash driver absence, DT property propagation, and AV preference reads validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/os-area.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/platform.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/platform.h

### Purpose
`platform.h` declares internal PS3 platform interfaces for HTAB, memory, IRQ, SMP, time, OS area, SPU, repository access, and device discovery.

### Important APIs, Types, And Functions
It declares PS3 init/shutdown functions, repository enums `ps3_bus_type`, `ps3_dev_type`, `ps3_interrupt_type`, `ps3_reg_type`, `ps3_spu_resource_type`, `struct ps3_repository_device`, and many `ps3_repository_read/find/write_*` helpers. It also provides config-dependent inline stubs for SMP cleanup, SPU setup, and repository writes.

### Control Flow
The header has no runtime flow but shapes compile-time paths through `CONFIG_SMP`, `CONFIG_SPU_BASE`, and `CONFIG_PS3_REPOSITORY_WRITE`.

### State, Persistence, And Dependencies
It stores no state. The declarations describe persistent external state in the PS3 repository, LV1 virtual address space, IRQ mappings, time/RTC settings, OS area, and device inventory.

### Integration Points
Every PS3 platform source includes this header to share repository and subsystem contracts. Device-init, MM, HTAB, interrupt, OS-area, time, SMP, and SPU code depend on it.

### Risks
Prototype drift can break cross-file builds. Stubbed repository writes silently return success when write support is disabled, which callers must understand. Enum values must match firmware repository encodings.

### Test Signals
Full PS3 platform builds across config combinations, repository helper callers, and sparse/prototype checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/platform.h -->
