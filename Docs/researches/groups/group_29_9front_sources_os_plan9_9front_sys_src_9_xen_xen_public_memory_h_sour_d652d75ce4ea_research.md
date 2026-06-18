# Group Research: group_29_9front_sources_os_plan9_9front_sys_src_9_xen_xen_public_memory_h_sour_d652d75ce4ea

Scope: `Docs/research_subset_a.md` subset A, covering 9front Xen public ABI/support files and Zynq kernel platform files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/memory.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/memory.h

Purpose: Xen public memory-management ABI header. It defines `HYPERVISOR_memory_op` command numbers and payload layouts for reservation changes, physical map updates, machine memory maps, populate-on-demand targets, paging/access/sharing operations, and memory claims.

Key interfaces:
- `xen_memory_reservation`, `xen_memory_exchange`, `xen_machphys_mfn_list`, `xen_machphys_mapping`.
- `xen_add_to_physmap`, `xen_add_to_physmap_range`, `xen_remove_from_physmap`.
- `xen_memory_map`, `xen_foreign_memory_map`, `xen_pod_target`.
- Tool/hypervisor-only event/sharing structs under `__XEN__ || __XEN_TOOLS__`.

Integration notes: Included by Xen-facing kernel code that needs allocation/deallocation or grant/foreign mapping semantics. This 9front tree uses `XENMEM_decrease_reservation` in `xensystem.c` when donating a frame.

Risk/attention points: This is an ABI contract; field widths, guest-handle macros, and interface-version conditionals must remain in sync with the Xen headers expected by the hypervisor.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/nmi.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/nmi.h

Purpose: Xen public NMI ABI header. It defines x86 NMI reason bits and the `nmi_op` commands used to register or unregister a callback.

Key interfaces:
- Reason bits: I/O error, PCI SERR, legacy parity alias, unknown NMI.
- `XENNMI_register_callback` with `xennmi_callback.handler_address`.
- `XENNMI_unregister_callback`.

Integration notes: Depends on `xen.h` for guest handles and Xen integer types. Primarily useful to privileged/dom0 code.

Risk/attention points: Callback registration is documented as meaningful only for dom0 vcpu0; other callers receive `EINVAL`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/nmi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/physdev.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/physdev.h

Purpose: Xen public physical-device operation ABI. It describes `physdev_op` commands for IRQ EOI/status, I/O privilege, APIC access, PIRQ mapping, PCI device registration, MSI/MSI-X coordination, GSI setup, and debug-port reset coordination.

Key interfaces:
- IRQ structs: `physdev_eoi`, `physdev_irq_status_query`, `physdev_irq`.
- Privilege/APIC structs: `physdev_set_iopl`, `physdev_set_iobitmap`, `physdev_apic`.
- PIRQ/PCI structs: `physdev_map_pirq`, `physdev_unmap_pirq`, `physdev_manage_pci*`, `physdev_pci_device_add`, `physdev_pci_device`.
- Compatibility aliases for pre-`0x00030202` names and version-dependent `PHYSDEVOP_pirq_eoi_gmfn`.

Integration notes: Depends on `xen.h`. Intended for privileged guests that own or mediate physical devices.

Risk/attention points: Several operations are version-sensitive or obsolete. Consumers must select the correct EOI-gmfn command based on `__XEN_INTERFACE_VERSION__`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/physdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/platform.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/platform.h

Purpose: Xen public dom0 platform-operation ABI. It defines `xen_platform_op` and subcommands for host clock, MTRR/memory types, microcode, EFI runtime calls, firmware information, ACPI sleep, CPU frequency/idle/power management, CPU online/offline/hot-add, memory hot-add, and core parking.

Key interfaces:
- `XENPF_INTERFACE_VERSION`.
- Payloads such as `xenpf_settime`, `xenpf_add_memtype`, `xenpf_efi_runtime_call`, `xenpf_firmware_info`, `xenpf_enter_acpi_sleep`, `xenpf_getidletime`, `xenpf_set_processor_pminfo`.
- Top-level `xen_platform_op` union with a 128-byte pad.

Integration notes: Includes `xen.h` and is intended for privileged domain-0 kernel/control code.

Risk/attention points: The union mixes many architecture- and firmware-specific layouts. ABI padding and interface version must be preserved exactly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/platform.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/sched.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/sched.h

Purpose: Xen public scheduler-operation ABI. It defines `HYPERVISOR_sched_op` command numbers and payloads for yield, block, shutdown, event-channel polling, remote shutdown, shutdown code latching, and watchdog management.

Key interfaces:
- `sched_shutdown`, `sched_poll`, `sched_remote_shutdown`, `sched_watchdog`.
- Shutdown reasons: poweroff, reboot, suspend, crash, watchdog.

Integration notes: Includes `event_channel.h`. 9front Xen code uses `SCHEDOP_yield`, `SCHEDOP_block`, and `SCHEDOP_shutdown` wrappers in `xensystem.c`.

Risk/attention points: `SCHEDOP_shutdown` suspend has special extra-argument semantics; simple wrappers must not assume all shutdown reasons are identical.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/sysctl.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/sysctl.h

Purpose: Xen public system-control ABI for node control tools. It is explicitly gated to `__XEN__` or `__XEN_TOOLS__` and defines `xen_sysctl` operations for host console, trace buffers, physical host info, scheduler info, performance counters, domain lists, debug keys, CPU info, heap availability, power management, page offlining, lock profiling, topology/NUMA info, CPU pools, scheduler tuning, and coverage data.

Key interfaces:
- `XEN_SYSCTL_INTERFACE_VERSION`.
- Many operation structs, including `xen_sysctl_readconsole`, `xen_sysctl_tbuf_op`, `xen_sysctl_physinfo`, `xen_sysctl_getdomaininfolist`, `xen_sysctl_get_pmstat`, `xen_sysctl_pm_op`, `xen_sysctl_page_offline_op`, `xen_sysctl_lockprof_op`, `xen_sysctl_topologyinfo`, `xen_sysctl_numainfo`, `xen_sysctl_cpupool_op`, `xen_sysctl_scheduler_op`, `xen_sysctl_coverage_op`.
- Top-level `xen_sysctl` command union with 128-byte padding.

Integration notes: Depends on `xen.h` and `domctl.h`; not ordinary guest ABI.

Risk/attention points: The header enforces control-tool-only use via preprocessor error. Any 9front build path including it must define the correct Xen tool/hypervisor macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/tmem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/tmem.h

Purpose: Xen public Transcendent Memory ABI header. It defines commands and payloads for tmem pools and page/object operations.

Key interfaces:
- Commands: `TMEM_CONTROL`, `TMEM_NEW_POOL`, `TMEM_PUT_PAGE`, `TMEM_GET_PAGE`, `TMEM_FLUSH_PAGE`, `TMEM_READ`, `TMEM_WRITE`, `TMEM_XCHG`.
- Privileged commands: `TMEM_AUTH`, `TMEM_RESTORE_NEW`.
- Control subops for freeze/thaw/flush/destroy/list/save/restore.
- `tmem_op` with `creat`, `ctrl`, and generic `gen` union arms; `tmem_handle`.

Integration notes: Depends on `xen.h`; guarded for non-assembly C definitions.

Risk/attention points: Special errno values `EFROZEN` and `EEMPTY` are ABI-level values and may collide with local errno assumptions if not handled distinctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/tmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/trace.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/trace.h

Purpose: Xen public tracing ABI header. It defines trace class/event IDs and the trace-buffer record layout used by Xen trace consumers.

Key interfaces:
- Trace class masks for general, scheduler, dom0 ops, HVM, memory, PV, shadow, hardware, guest.
- Scheduler subclass encoding and per-scheduler event helper macro.
- Event IDs for scheduler, memory, PV hypercalls/traps, shadow, HVM exits/handlers, power management, and IRQ handling.
- Record structs: `t_rec`, `t_buf`, `t_info`.

Integration notes: Used by control tools that map Xen trace buffers obtained via sysctl tbuf operations.

Risk/attention points: The trace record bitfields and flexible-array metadata are ABI structures. Consumers must understand optional cycle-count inclusion and `extra_u32` lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/vcpu.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/vcpu.h

Purpose: Xen public VCPU operation ABI. It defines operations for VCPU initialization, up/down, runstate queries, shared runstate/time registration, VCPU timers, NMI sending, and physical ID lookup.

Key interfaces:
- `VCPUOP_initialise`, `VCPUOP_up`, `VCPUOP_down`, `VCPUOP_is_up`.
- `vcpu_runstate_info`, `vcpu_register_runstate_memory_area`.
- `vcpu_set_periodic_timer`, `vcpu_set_singleshot_timer`.
- `vcpu_register_vcpu_info`, `vcpu_get_physid`, `vcpu_register_time_memory_area`.

Integration notes: Depends on `xen.h`. 9front’s Xen timer code reads the shared `vcpu_time_info` through `shared_info` rather than using the registration op.

Risk/attention points: The comments document important hotplug race and memory-reference caveats; VCPU down is generally asynchronous unless self-invoked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/vcpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/version.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/version.h

Purpose: Xen public version-query ABI. It defines `HYPERVISOR_xen_version` command IDs and result structures.

Key interfaces:
- `XENVER_version`, `XENVER_extraversion`, `XENVER_compile_info`, `XENVER_capabilities`, `XENVER_changeset`, `XENVER_platform_parameters`, `XENVER_get_features`, `XENVER_pagesize`, `XENVER_guest_handle`, `XENVER_commandline`.
- Types for compile info, capabilities, changeset, platform parameters, feature submaps, and command line.

Integration notes: Includes `features.h`. 9front uses `HYPERVISOR_xen_version(0, 0)` as a harmless hypercall to provoke pending event delivery after unmasking.

Risk/attention points: Most commands return zero on success, but `XENVER_version` and `XENVER_pagesize` return direct values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen-compat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen-compat.h

Purpose: Xen public compatibility shim. It defines the latest supported interface version and default behavior for guests/tools that do not select an interface version.

Key interfaces:
- `__XEN_LATEST_INTERFACE_VERSION__` set to `0x00040300`.
- Tools/hypervisor builds force `__XEN_INTERFACE_VERSION__` to latest.
- Guests without a requested version get legacy `0x00000000`.
- Compile-time rejection if a requested version is newer than the headers.

Integration notes: Included first by `xen.h`, which drives many version conditionals in other public headers.

Risk/attention points: Changing this file affects ABI selection across the entire Xen header set.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen-compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen.h

Purpose: Core Xen public guest ABI header. It selects architecture-specific ABI headers, defines guest handles for primitive types, hypercall numbers, compatibility remaps, virtual IRQs, MMU update commands, VA mapping flags, console/vm-assist commands, domain IDs, multicall entries, event-channel shared state, time/shared-info structures, start-of-day boot layout, dom0 VGA console info, and helper typedefs/macros.

Key interfaces:
- Hypercall numbers `__HYPERVISOR_*`.
- VIRQ constants and `NR_VIRQS`.
- `mmuext_op`, `mmu_update`, `multicall_entry`.
- `vcpu_time_info`, `vcpu_info`, `shared_info`, `start_info`.
- Domain IDs: `DOMID_SELF`, `DOMID_IO`, `DOMID_XEN`, `DOMID_COW`, `DOMID_INVALID`, `DOMID_IDLE`.
- `xenctl_bitmap` for tool/sysctl use.

Integration notes: Central dependency for the other Xen public headers and Plan 9 Xen kernel code. `xensystem.c` uses hypercall numbers, MMU constants, event-channel state, domain IDs, and `start_info/shared_info`.

Risk/attention points: It mixes architecture selection, ABI constants, and shared-memory layouts. Any local type mismatch can break hypercall marshalling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xencomm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xencomm.h

Purpose: Xen public xencomm descriptor header. It defines a scatter/gather descriptor for platforms where the hypervisor needs physical addresses backing a virtually contiguous memory area.

Key interfaces:
- `XENCOMM_MAGIC`, `XENCOMM_INVALID`.
- `struct xencomm_desc` with `magic`, `nr_addrs`, and flexible `address[]`.

Integration notes: Standalone header, no includes in the file itself.

Risk/attention points: Consumers must allocate enough trailing address entries and fill physical addresses in hypervisor-expected order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xencomm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xenoprof.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xenoprof.h

Purpose: Xen public profiling ABI for XenOprofile/system-wide hardware counter profiling.

Key interfaces:
- `XENOPROF_*` commands from init/list setup/counter reservation/start/stop/shutdown/buffer/backtrace through AMD IBS support.
- `event_log`, `xenoprof_buf`, `xenoprof_init`, `xenoprof_get_buffer`, `xenoprof_counter`, `xenoprof_passive`, `xenoprof_ibs_counter`.

Integration notes: Depends on `xen.h`; profiling samples are delivered through shared per-VCPU buffers.

Risk/attention points: `xenoprof_buf` uses a one-element trailing `event_log` pattern; allocation sizing must account for actual sample capacity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xenoprof.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xsm/flask_op.h -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xsm/flask_op.h

Purpose: Xen XSM/FLASK security-module operation ABI. It defines command payloads for policy loading, enforcement, SID/context conversion, access checks, transitions, users, booleans, AVC stats, object contexts, peer SID lookup, and domain relabeling.

Key interfaces:
- `XEN_FLASK_INTERFACE_VERSION`.
- Payloads: `xen_flask_load`, `xen_flask_setenforce`, `xen_flask_sid_context`, `xen_flask_access`, `xen_flask_transition`, `xen_flask_userlist`, `xen_flask_boolean`, stats/relabel structs.
- Top-level `xen_flask_op` with `FLASK_*` command constants.

Integration notes: Assumes Xen guest-handle and event-channel types are already visible through including context; this file itself does not include `xen.h`.

Risk/attention points: The missing local include means include order matters. It should be included only after types like `XEN_GUEST_HANDLE` and `evtchn_port_t` are defined.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen-public/xsm/flask_op.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen.s -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xen.s

Purpose: Plan 9 x86 assembly glue for Xen callbacks and hypercall entry.

Key interfaces:
- `hypervisor_callback`: saves a Plan 9 `Ureg`-compatible frame, fixes segment registers, calls `xenupcall`, restores state, and returns with `IRETL`.
- `failsafe_callback`: nominal Xen failsafe callback path; currently begins with immediate `IRETL`, leaving later repair code unreachable.
- `xencall1` through `xencall6`: fall-through wrappers that load hypercall op/args into x86 registers and execute `INT $0x82`.

Integration notes: Used by `xensystem.c` hypercall wrappers. Includes `xendefs.h` and `mem.h`.

Risk/attention points: The source comments call out a race where an upcall can stack between `spllo()` and `rti`. The failsafe callback has unreachable handler-install code after `IRETL`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xen.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenbin.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xenbin.c

Purpose: User-space conversion tool that transforms a Plan 9 386 bootable image into a Xen binary-loader-compatible image.

Key behavior:
- Reads Plan 9 executable metadata with `crackhdr`.
- Pads text so the Xen image can load at guest physical address zero.
- Emits a Plan 9 header and 32-byte Xen binary header with magic/checksum/load addresses.
- Page-aligns data and adjusts line-number PC table encoding for debugger consistency.
- Optional `-p` sets the Xen PAE flag.

Integration notes: Uses Plan 9 libc/bio/mach headers and streams input from fd 0 to output fd 1.

Risk/attention points: It assumes valid `crackhdr` results and does little error checking on reads/writes. Arithmetic is 32-bit `long` oriented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenbin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenelf.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xenelf.c

Purpose: User-space ELF rewriter for Xen boot images. It page-aligns program segments and appends a named section containing supplied string contents.

Key behavior:
- Reads ELF header/program headers with explicit little-endian helpers.
- Copies loadable segments to page-aligned offsets and rounds `filesz`/`memsz` for `LOAD` segments.
- Copies extra symbol/line data for non-load segments using `memsz`.
- Appends a minimal section-name string table and one new section named by the caller.
- Rewrites ELF section-header metadata.

Integration notes: Invoked as `xenelf input output section-name section-contents`. Includes `/sys/src/libmach/elf.h`.

Risk/attention points: Existing section headers are effectively ignored (`ns = 0`), so the output is intentionally minimal. Error checking on I/O is sparse.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenelf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xengrant.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xengrant.c

Purpose: 9front Xen kernel grant-table manager for sharing or transferring page frames with other domains.

Key behavior:
- `xengrantinit` sets up one grant-table frame via `GNTTABOP_setup_table`, maps it at `XENGRANTTAB`, and initializes a simple freelist of grant refs.
- `xengrant` allocates a ref, fills frame/domain, enforces ordering via `coherence()`, then publishes grant flags.
- `xengrantend` validates no active use or incomplete transfer, invalidates flags, frees the ref, and returns the frame.

Integration notes: Used by `xensystem.c` for `shareframe`, `donateframe`, and `acceptframe`.

Risk/attention points: `Nframes` is hardcoded to 1 and comments warn not to increase it without extra mappings. Exhaustion panics rather than returning an error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xengrant.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenstore.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xenstore.c

Purpose: Small Plan 9 user-space Xenstore command-line client.

Key behavior:
- Implements Xenstore wire message header `xsd_sockmsg` and command enum.
- `xscmd` sends one request and reads one response using a static 512-byte buffer.
- Commands: read, list directory, mkdir, delete, write, and watch.
- Binds `#x` onto `/dev` if `/dev/xenstore` is missing.
- Watch mode subscribes through `/dev/xenstore`, then reads events from `/dev/xenwatch`.

Integration notes: Talks to Plan 9 Xen device files rather than directly to Xen shared pages.

Risk/attention points: The static buffer bounds are not checked against path/value/response sizes. It prints response header diagnostics to fd 2 for every command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xenstore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xensystem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xensystem.c

Purpose: Core 9front Xen kernel integration layer. It wraps Xen hypercalls, manages Xen-specific page-table operations, handles event-channel upcalls, grants/transfers frames, and implements interrupt masking/channel helpers.

Key behavior:
- Hypercall wrappers call `xencall1`-`xencall6` for MMU, sched, event channel, Xen version, console, grant table, and memory ops.
- Maintains Xen globals: `xenstart`, `HYPERVISOR_shared_info`, `patomfn`, `matopfn`, `hypervisor_virt_start`, `xentop`.
- Page-table helpers pin/unpin L1/L2/L3 tables, switch base pointer, flush TLB, and update PTEs with machine-address translations.
- Grant helpers: `acceptframe`, `donateframe`, `shareframe`.
- `xenupcall` drains pending event-channel bits and dispatches them through Plan 9 `trap` with vector `100+port`.
- Interrupt glue binds VIRQs/channels, masks/unmasks event-channel bits, and implements `spllo`, `splhi`, `splx`, `islo`.
- Channel helpers allocate unbound ports and notify peers; `halt` blocks via Xen scheduler when idle.

Integration notes: Depends on Xen public headers/types, Plan 9 MMU/trap/intr code, and assembly hypercall stubs in `xen.s`.

Risk/attention points: Several wrappers panic on failure. Comments note possible efficiency improvement via multicall and uncertainty about return-value handling. Event upcall masking is subtle and must preserve Xen pending/mask ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xensystem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xentimer.c -->
# File Research: sources/os/plan9/9front/sys/src/9/xen/xentimer.c

Purpose: 9front Xen timer implementation using Xen shared `vcpu_time_info` and Xen timer VIRQ.

Key behavior:
- `getshadow` reads a consistent copy of per-VCPU time info using Xen version sequencing.
- `xentimerinit` derives CPU frequency from Xen TSC conversion parameters.
- `xentimerset` arms Xen timer with a minimum lead time.
- `xentimerenable` binds `VIRQ_TIMER`.
- `xentimerread` converts TSC cycles to nanoseconds and tracks wallclock base from shared info.
- Provides `xenwallclock`, `microdelay`, `delay`, and `perfticks`.

Integration notes: Uses `HYPERVISOR_shared_info`, `HYPERVISOR_set_timer_op`, `cycles`, `mul64fract`, and Plan 9 timer interrupt code.

Risk/attention points: `getshadow` spins while version is odd; correctness depends on Xen’s seqlock-style update protocol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/xen/xentimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/dat.h

Purpose: Zynq ARM kernel machine data definitions for 9front.

Key interfaces:
- Core typedef declarations for kernel structs.
- `Label`, `FPsave`, `PFPU`, `Confmem`, `Conf`, `PMMU`, `L1`, `MMMU`, `Mach`, `ISAConf`, `DevConf`.
- FPU states and `NCOLOR`.
- Global `active`, register variables `m` and `up`, and MMIO globals `mpcore`, `slcr`.

Integration notes: Includes `../port/portdat.h`, so it anchors platform-specific structures before portable kernel data.

Risk/attention points: `Mach` layout has an “end of known to assembly” boundary; assembly files depend on early field offsets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/devarch.c

Purpose: Zynq-specific `#P/arch` device exposing CPU temperature, FPGA programmable-logic configuration, and framebuffer control.

Key behavior:
- `xadcinit`, `xadcirq`, and `xadctimer` configure/read XADC temperature and trigger shutdown-like `scram` at extreme temperature.
- PL support maps an AXI physical segment, configures device-controller interrupts, waits for INIT/DONE, and streams bitstream data through DMA.
- Device files: `cputemp`, `pl`, `fbctl`.
- `archread` returns temperature, waits for PL done, or delegates to framebuffer control.
- `archwrite` programs PL or delegates framebuffer control.
- `archinit` unlocks SLCR and initializes XADC/PL.

Integration notes: Uses `slcr`, `vmap`, interrupt framework, Plan 9 dev helpers, physical segment registration, and screen framebuffer functions.

Risk/attention points: Temperature thresholds cause printed warnings and eventually call `scram`. PL write path requires 4-byte aligned, positive lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/devqspi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/devqspi.c

Purpose: Zynq QSPI flash device driver exposed as `#Q/qspi`, with a `boot` file representing the boot flash area.

Key behavior:
- Maps QSPI controller registers and configures linear QSPI mode off/manual SPI mode on.
- `qspicmd` sends 1-4 byte commands and returns RX data.
- `doread` issues fast-read command `0x6B` with dummy cycle and reads up to 16 MiB.
- `dowrite` issues write-enable and quad page-program `0x32` in 256-byte chunks.
- `doerase` erases sector/block at an address.
- Opening `boot` with truncate erases address 0; reads/writes are serialized by `qspil`.

Integration notes: Uses Plan 9 device framework and `vmap`.

Risk/attention points: Buffer addresses must be word aligned. Partial write handling is delicate; the short tail path passes a variable that should be reviewed if arbitrary byte counts are expected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/devqspi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/emmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/emmc.c

Purpose: Zynq eMMC/SD host controller driver for the portable Plan 9 SDIO layer.

Key behavior:
- Maps SDIO controller, resets host, configures clock, enables interrupt.
- Implements SDIO callbacks: init, enable, inquiry, command, DMA setup, I/O completion, bus width/speed.
- `emmccmd` builds command-transfer mode bits from `SDiocmd`, handles command/data inhibit recovery, reads responses, and waits for busy completion.
- `emmciosetup` configures system DMA address and block count/size with cache clean.
- `emmcio` waits for data completion, checks errors, and invalidates caches after reads.
- `emmclink` registers the controller via `addmmcio`.

Integration notes: Depends on `../port/sd.h`, interrupt handling, cache maintenance helpers, and physical address conversion.

Risk/attention points: Uses timeout sleeps for data completion. DMA length is capped by controller limits and assumes buffers are physically addressable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/emmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/etherzynq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/etherzynq.c

Purpose: Zynq GEM Ethernet driver for 9front’s `etherif` layer.

Key behavior:
- Defines GEM, PHY, DMA descriptor, and SLCR clock constants.
- MDIO read/write helpers wait for PHY idle.
- `ethproc` monitors link, configures 10/100/1000 speed, duplex, and GEM clock divisors.
- RX ring replenishes `Block`s, handles DMA descriptor ownership, invalidates caches, and queues packets.
- TX path pulls from output queue, cleans caches, fills descriptors, and starts transmit.
- Interrupt handler processes management completion, TX, RX, RX-used, and overrun events.
- Supports promiscuous mode and multicast hash programming.
- `etherpnp` creates a single controller with default MAC and registers it.

Integration notes: Uses Plan 9 network interface APIs, `vmap`, `xspanalloc`, `ucalloc`, cache maintenance, and Zynq SLCR clock registers.

Risk/attention points: Static default MAC is hardcoded. Descriptor/cache ordering depends on explicit `coherence()` and cache maintenance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/etherzynq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/fns.h

Purpose: Zynq platform function declarations and machine macros.

Key interfaces:
- Address helpers: `kaddr`, `paddr`, `cankaddr`, `KADDR`, `PADDR`.
- Process/MMU/cache functions: `procsave`, `procrestore`, `kmap`, `kunmap`, `mmuinit`, `ttbget/put`, `vmap`, `tmpmap`, `flushpg`, `setasid`, `flushtlb`.
- Interrupt/timer/device init declarations.
- ARM cache maintenance and DMA helpers.
- Screen, architecture, and config declarations.

Integration notes: Includes `../port/portfns.h` and is consumed by most Zynq C files.

Risk/attention points: Header must match assembly exports in `l.s`; mismatches would fail at link time or cause ABI bugs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/init9.s

Purpose: Tiny Plan 9 ARM startup adapter that jumps into `startboot`.

Key behavior:
- Sets static base register `R12`.
- Moves boot arguments from stack/registers into expected positions.
- Branches to `startboot`.

Integration notes: This is an early entry shim before the broader Zynq assembly startup in `l.s`.

Risk/attention points: It relies on exact calling/stack convention at kernel entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/intr.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/intr.c

Purpose: Zynq interrupt controller driver for the ARM GIC.

Key behavior:
- `intrinit` enables distributor/CPU interface and disables/clears all interrupts on CPU0.
- `intrenable` validates IRQ/type, assigns target CPU for shared interrupts, configures level/edge trigger, priority, handler, and enables the interrupt.
- `intr` reads interrupt acknowledge, dispatches registered handler, writes EOI, and returns whether it was the timer IRQ.

Integration notes: Uses `mpcore` MMIO mapping, `Ureg`, Plan 9 interrupt accounting, and constants from `io.h`.

Risk/attention points: Only one handler function is allowed per IRQ unless it is the same function. IRQ target programming currently selects CPU0 for non-private interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/io.h

Purpose: Zynq platform MMIO base-address and IRQ-number definitions.

Key interfaces:
- Base addresses for UART, USB, Ethernet, QSPI, SDIO, SLCR, DEVC, MPCORE, L2, OCM.
- IRQ numbers for timer, XADC, device config, USB, Ethernet, SDIO, UART.
- Interrupt trigger constants `LEVEL`, `EDGE`.
- `PS_CLK` and `XADCINTERVAL`.

Integration notes: Included by most Zynq platform drivers and assembly startup.

Risk/attention points: These constants encode the board/platform memory map; wrong values break early boot or device access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/l.s

Purpose: Main Zynq ARM assembly support file: early boot, MMU/cache setup, CPU bootstrap, user transitions, synchronization primitives, TLB/cache maintenance, performance counters, and VFP save/restore.

Key behavior:
- `_start` clears config space, builds initial section/page mappings, maps UART for debug output, enables MMU, and jumps to virtual address space.
- `_virt` sets stacks, vector base, VFP permissions, L1 cache, TPIDRPRW Mach pointer, and calls `main`.
- `mpbootstrap` starts CPU1 using its own Mach/L1 setup.
- `touser` and `forkret` restore user state.
- Implements `spllo`, `splhi`, `splx`, `islo`, labels, CAS/TAS, barriers, idle/event instructions.
- Implements TTB/TLB/FAR/FSR accessors, performance counter access, cycle counter high-word maintenance, VFP init/save/restore/off.
- Implements cache clean/invalidate operations by range and line.

Integration notes: Exports many functions declared in `fns.h`; depends on offsets/layout in `mem.h` and `dat.h`.

Risk/attention points: Assembly depends on exact `Mach` offsets and ARM control-register semantics. Early UART debug writes assume a specific UART MMIO address.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/ltrap.s -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/ltrap.s

Purpose: Zynq ARM exception vector and trap/syscall entry assembly.

Key behavior:
- `vectors` branches reset/undefined/SVC/prefetch abort/data abort/IRQ/FIQ slots to handlers.
- Exception paths save SPSR/CPSR/LR and general registers into a `Ureg` frame, reload Mach/up from TPIDRPRW, and call `trap`.
- SVC path builds syscall frame and calls `syscall`.
- Return paths restore SPSR/registers and return to user or interrupted mode.

Integration notes: Uses `mem.h` processor-mode constants and Plan 9 `trap`/`syscall` C handlers.

Risk/attention points: Correct frame shape is critical for `trap`, `syscall`, and `userureg` interpretation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/ltrap.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/main.c

Purpose: Zynq kernel initialization and platform lifecycle code.

Key behavior:
- `exit` shuts down CPUs, clears private pages on CPU0, and idles forever.
- L2 cache setup and physical-cache maintenance helpers.
- `options` parses boot configuration at `CONFADDR`.
- `confinit` defines memory/process/page-pool sizing for a 1 GiB system.
- `init0` initializes devices/environment and enters user `boot`.
- `mpinit` optionally starts CPU1 via OCM bootstrap pointer and synchronizes counters.
- `main` performs platform boot sequence: UART/MMU/L2/intr/options/conf/timer/print/proc/segments/links/arch/devices/page/screen/user/scheduler.
- Stubs `reboot`, `isaconfig`, `setupwatchpts`.

Integration notes: Coordinates almost every Zynq subsystem and portable Plan 9 kernel initialization.

Risk/attention points: Memory sizing is hardcoded around 1 GiB. Multiprocessor startup can be disabled with `*nomp`; otherwise CPU1 setup relies on OCM bootstrap conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/mem.h

Purpose: Zynq ARM memory-layout, page-table, processor-state, and assembly macro definitions shared by C and assembly.

Key interfaces:
- Page/cache sizes, `MAXMACH`, `KSTACK`, `HZ`.
- Kernel/user virtual layout: `KZERO`, `KTZERO`, `VMAP`, `TMAP`, `KMAP`, `MACH`, `MACHL1`, `CONFADDR`, `USTKTOP`.
- PTE/L1/L2 constants and index macros.
- ARM CPSR mode bits and barrier/instruction macros.
- Register assignments `Rmach` and `Rup`.
- VFP register access macros and translation table attributes.

Integration notes: Included by all Zynq assembly and many C files.

Risk/attention points: This file is the contract for virtual memory layout and assembly constants; changes require coordinated updates across MMU, trap, and boot code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/mmu.c

Purpose: Zynq ARM MMU, mapping, and cache-address helper implementation.

Key behavior:
- `mmuinit` records current L1 table, installs per-CPU temp-map L2, and maps MPCORE/SLCR/OCM once.
- `l1switch`, `l1alloc/free`, and `upallocl1` manage per-process L1 tables and ASIDs.
- `l2free`, `mmuswitch`, `putmmu`, `flushmmu`, `mmurelease` manage user mappings and process MMU lifetime.
- `paddr`, `kaddr`, `cankaddr` convert between virtual and physical spaces for direct, VMAP, and OCM ranges.
- `kmap/kunmap` provide temporary per-process kernel mappings.
- `tmpmap/tmpunmap` provide per-CPU temporary mappings with interrupts high.
- `vmap` maps device MMIO as uncached/device/noexec.
- `ucalloc` allocates uncached memory from OCM for DMA descriptors/buffers.

Integration notes: Uses page allocator, process state, cache/TLB assembly helpers, `mpcore/slcr/ocm` globals, and Plan 9 VM conventions.

Risk/attention points: Temporary mappings panic if used at low interrupt priority. `ucalloc` is a simple downward allocator from OCM and does not free.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/screen.c

Purpose: Zynq software framebuffer bridge and hardware cursor/control integration for Plan 9 draw/mouse code.

Key behavior:
- Maintains `gscreen` as a `Memimage` backing screen.
- `flushmemscreen` coalesces dirty rectangles and wakes the framebuffer copy process.
- `attachscreen` exposes the software screen to draw.
- `fbctlwrite` handles framebuffer control commands: `addr`, `size`, `init`.
- `screenproc` copies dirty regions from `gscreen` into a user-provided framebuffer-mapped segment.
- `mousectl` handles cursor register address and acceleration mode.
- `cursorproc` writes hardware cursor bitmap and position registers.
- `fbctlread` reports current size/channel and framebuffer address.

Integration notes: `devarch.c` exposes `fbctl`; `screen.h` declares this file’s hooks for portable draw/mouse code.

Risk/attention points: Framebuffer and cursor MMIO addresses are supplied through user segments and validated for writability/range. Helper kprocs are killed/restarted when addresses change.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/screen.h

Purpose: Zynq screen/mouse integration header for portable Plan 9 draw and mouse code.

Key interfaces:
- Mouse declarations: cursor, mouse tracking, acceleration, serial mouse byte handlers, `mousectl`, redraw/resize.
- Screen declarations: blanking, flushing, attaching, cursor operations.
- Draw declarations: `deletescreenimage`, `resetscreenimage`, `drawlock`.
- Defines `ishwimage(i)` as always true for `devdraw.c`.

Integration notes: Included by `screen.c` and expected by draw/mouse drivers.

Risk/attention points: `ishwimage(i) 1` means all images are treated as hardware images in the relevant portable code path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/timer.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/timer.c

Purpose: Zynq ARM timer and cycle-counter implementation.

Key behavior:
- `fastticks` reads the global timer high/low registers consistently and reports `timerhz`.
- `µs`, `microdelay`, and `delay` provide busy-wait timing.
- `timerset` programs the local timer for the next kernel timer deadline, clamping to 32-bit range.
- `timerirq` acknowledges local timer interrupt and calls `timerintr`.
- `timerinit` derives CPU/timer frequencies from SLCR PLL/clock registers, enables global/local timers, registers clock IRQ, and enables performance counters.
- `synccycles` synchronizes cycle counters across CPUs using two `Ref` barriers.

Integration notes: Uses `mpcore`, `slcr`, interrupt setup, performance-counter assembly helpers, and Plan 9 timer subsystem.

Risk/attention points: `synccycles` assumes all configured CPUs enter the barrier; incorrect `conf.nmach` or failed CPU startup would hang.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/timer.c -->