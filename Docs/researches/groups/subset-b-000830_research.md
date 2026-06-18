# subset-b-000830 research

Work item `subset-b-000830` covers s390 KVM support files plus adjacent s390 architecture library and memory-management helpers. Each file section below is bounded by the exact reconciliation markers required for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.h

## Purpose
Central private header for s390 KVM implementation. It provides shared inline helpers, logging macros, instruction decoding helpers, and cross-file prototypes used by intercept handling, interrupt delivery, protected virtualization, nested SIE, PCI interpretation, debug support, and core VM lifecycle code.

## Important APIs, Types, And Functions
`union kvm_s390_quad` exposes sized aliases for instruction data. `kvm_s390_fpu_store()` and `kvm_s390_fpu_load()` bridge KVM run-state floating-point/vector state with host FPU helpers. CPU flag helpers (`kvm_s390_set_cpuflags()`, `kvm_s390_clear_cpuflags()`, `kvm_s390_test_cpuflags()`) operate atomically on the SIE block. Address decoders (`kvm_s390_get_base_disp_s()`, `*_siy()`, `*_sse()`, `*_rsy()`, `*_rs()`, `kvm_s390_get_regs_rre()`) interpret the intercepted instruction bytes in `ipa`/`ipb`. `kvm_s390_set_prefix()`, `kvm_s390_rewind_psw()`, `kvm_s390_forward_psw()`, and `kvm_s390_retry_instr()` encapsulate common PSW/SIE request manipulation. The header also declares all major subsystem entry points: PV in `pv.c`, privileged instruction handlers in `priv.c`, nested SIE in `vsie.c`, SIGP in `sigp.c`, interrupts, diagnostics, guest debug, PCI interpretation, and core kvm-s390 functions.

## Control Flow And State
Most functions are small inline control-flow adapters around `struct kvm`, `struct kvm_vcpu`, `vcpu->arch.sie_block`, and `vcpu->run->s.regs`. Prefix changes update the SIE block then enqueue TLB and guest-prefix refresh requests. Program-interrupt helpers convert guest access return codes into injected KVM s390 IRQs only when the error came from guest memory translation. PV page destruction handles races by trying an export if secure-page destruction fails.

## Dependencies And Integration
The header depends heavily on Linux KVM host APIs, s390 facility detection, SIE layout, gmap, DAT, SCLP, UV, and debug feature infrastructure. It is included by most files under `arch/s390/kvm/`, so changes to inline semantics have broad blast radius.

## Risks And Test Signals
High-risk areas include PSW address rewinding, signed displacement decoding, atomic CPU flags, secure-page race handling, and facility gating. Tests are mostly integration-level: KVM selftests, s390 guest boot/intercept tests, protected virtualization flows, and trace/debug validation. Compile-time type and prototype breakage is also an important signal because this header is central.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pci.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/pci.c

## Purpose
Implements s390 KVM zPCI passthrough support for VFIO zdev devices, including adapter event notification interpretation, adapter interruption forwarding, and registration of a zPCI device with a specific KVM VM for load/store interpretation.

## Important APIs, Types, And Functions
The exported/externally referenced functions are `kvm_s390_pci_aen_init()`, `kvm_s390_pci_aen_exit()`, `kvm_s390_pci_init_list()`, `kvm_s390_pci_clear_list()`, `kvm_s390_pci_zpci_op()`, `kvm_s390_pci_init()`, and `kvm_s390_pci_exit()`. Static helpers set/reset the global AIPB (`zpci_setup_aipb()`, `zpci_reset_aipb()`), register/deregister floating adapter IRQ forwarding (`kvm_zpci_set_airq()`, `kvm_zpci_clear_airq()`), account pinned guest pages against `RLIMIT_MEMLOCK`, enable/disable AIF, and attach/detach `struct kvm_zdev` to `struct zpci_dev`.

## Control Flow And State
`kvm_s390_pci_init()` installs `zpci_kvm_hook` callbacks and allocates the global `aift` if interpretation is allowed. `kvm_s390_pci_register_kvm()` is called by zPCI/VFIO registration, opens a `kvm_zdev`, enables VM-wide PCI interpretation on first use, programs `zdev->gisa`, re-enables the device, and links it into `kvm->arch.kzdev_list`. `kvm_s390_pci_zpci_op()` dispatches userspace zPCI operations by function handle, currently register/deregister AEN. AIF enable pins guest AIBV/AISB pages, allocates an AIFT summary bit, fills a GAITE, rewrites the FIB for host forwarding, then issues the zPCI modify function. Disable reverses firmware registration, frees the summary bit/vector, unpins pages, unregisters GISC, and clears saved FIB state.

## Dependencies And Integration
Integrates Linux KVM, VFIO zPCI hooks, s390 zPCI CLP/mod-fc firmware calls, GISA/GISC interrupt routing, adapter interruption vectors, SCLP capability detection, and KVM VM locking/list state.

## Risks And Test Signals
Risks center on pinned-page accounting leaks, lock ordering across `kvm->lock`, `zdev->kzdev_lock`, and `aift` locks, stale global AIPB state across module unload/reload, failure rollback, and forced cleanup when devices disappear. Signals include VFIO zPCI passthrough tests, module load/unload with AEN, guest MSI delivery, memlock accounting, lockdep, and KVM zPCI ioctl error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pci.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/pci.h

## Purpose
Private header for s390 KVM zPCI passthrough. It defines the KVM-side zPCI tracking objects, the global adapter interruption forwarding table shape, and declarations consumed by KVM core and PCI implementation code.

## Important APIs, Types, And Functions
`struct kvm_zdev` binds a `struct zpci_dev` to a `struct kvm`, stores the guest/host FIB used for adapter interruption forwarding, and links into `kvm->arch.kzdev_list`. `struct zpci_gaite` models a guest adapter interrupt table entry containing GISA, GISC, reference count, AISB offset, and AISB address. `struct zpci_aift` holds the global GAIT, summary-bit vector, per-summary-index `kvm_zdev` map, and two locks: `gait_lock` for interrupt-side GAIT access and `aift_lock` for broader table lifecycle. `kvm_s390_pci_si_to_kvm()` maps an adapter summary index to the associated VM if CONFIG support and table state exist. `kvm_s390_pci_interp_allowed()` gates support on config, SCLP facilities, and known machine IDs without SHM.

## Control Flow And State
The header is declarative but encodes the persistent state model: one global `aift`, per-VM zdev lists, per-device saved FIB state, and feature gating before interpretation setup. The machine-ID denylist short-circuits even if general zPCI facilities are present.

## Dependencies And Integration
Depends on Linux KVM host structures, PCI/zPCI definitions, s390 AIRQ vectors, CPU ID, and SCLP feature flags. Consumers include `pci.c`, KVM VM init/teardown, and interrupt delivery paths that need to recover a KVM from a zPCI summary bit.

## Risks And Test Signals
Risks include stale `aift->kzdev` lookups, summary-index bounds assumptions, mismatched feature gating between header and implementation, and use after free during module exit or interrupt delivery. Test signals are zPCI passthrough initialization on supported/unsupported machine models, AEN forwarding, lockdep, and compile coverage for CONFIG_VFIO_PCI_ZDEV_KVM on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/priv.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/priv.c

## Purpose
Emulates or routes privileged s390 instructions intercepted from a KVM guest. It covers facility lazy-enablement, clock/prefix/control-register handling, storage keys, I/O instruction exits, AP crypto queue instructions, PSW loading, STSI/STFL/STIDP, CMMA ESSA/PFMF, TPROT, and opcode group dispatchers.

## Important APIs, Types, And Functions
External entry points include `is_valid_psw()`, `kvm_s390_handle_aa()`, `kvm_s390_handle_e3()`, `kvm_s390_handle_b2()`, `kvm_s390_handle_b9()`, `kvm_s390_handle_lpsw()`, `kvm_s390_handle_lctl()`, `kvm_s390_handle_stctl()`, `kvm_s390_handle_eb()`, `kvm_s390_handle_e5()`, `kvm_s390_handle_01()`, and `kvm_s390_skey_check_enable()`. Major static handlers include `handle_set_clock()`, `handle_set_prefix()`, `handle_iske()/rrbe()/sske()`, `handle_tpi()/tsch()/io_inst()`, `handle_pqap()`, `handle_lpswe()/lpswey()`, `handle_stsi()`, `handle_pfmf()`, `handle_essa()`, `handle_lctlg()/stctg()`, `handle_tprot()`, and `handle_sckpf()/ptff()`.

## Control Flow And State
Dispatch starts from opcode-group handlers keyed by `ipa` or `ipb` low bits. Each handler validates privilege state, operand alignment, facility availability, and guest memory access. Guest memory faults are converted with `kvm_s390_inject_prog_cond()` when appropriate; some instructions exit to userspace via `-EOPNOTSUPP` or `-EREMOTE` with populated `vcpu->run` payloads. Lazy enablement sets SIE control bits and rewinds the PSW for retry. Storage-key and CMMA paths update gmap/DAT state under MMU locks, top up MMU caches on `-ENOMEM`, and may modify guest registers or condition codes.

## Dependencies And Integration
Depends on gaccess, gmap/DAT helpers, KVM interrupt injection, AP crypto hooks, SCLP/facility bits, lowcore layouts, tracepoints, sysinfo/STSI, and userspace KVM exits for channel I/O and user STSI.

## Risks And Test Signals
Risks are precise architecture semantics: wrong condition codes, PSW advancement, low-address protection, DAT/IPTE locking, facility masking, PV SIDA behavior for STSI, and incorrect userspace exit payloads. Useful signals include s390 KVM selftests, guest boot with channel I/O, storage-key/CMMA tests, AP/VFIO tests, protected guest STSI, tracepoint coverage, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pv.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/pv.c

## Purpose
Implements s390 KVM protected virtualization host support. It creates/destroys secure VM and secure CPU objects with Ultravisor calls, imports/unpacks/destroys secure pages, supports asynchronous protected-VM teardown, tracks mm lifetime, and provides dump operations for protected guests.

## Important APIs, Types, And Functions
Exports include `kvm_s390_pv_is_protected()` and `kvm_s390_pv_cpu_is_protected()`. Core entry points declared in `kvm-s390.h` include `kvm_s390_pv_init_vm()`, `kvm_s390_pv_deinit_vm()`, `kvm_s390_pv_set_aside()`, `kvm_s390_pv_deinit_aside_vm()`, `kvm_s390_pv_deinit_cleanup_all()`, `kvm_s390_pv_create_cpu()`, `kvm_s390_pv_destroy_cpu()`, `kvm_s390_pv_make_secure()`, `kvm_s390_pv_convert_to_secure()`, `kvm_s390_pv_destroy_page()`, `kvm_s390_pv_unpack()`, `kvm_s390_pv_set_sec_parms()`, `kvm_s390_pv_set_cpu_state()`, and protected dump helpers.

## Control Flow And State
VM initialization registers an mmu notifier once, allocates base and variable UV storage sized from memslots, disables huge pages, splits existing huge mappings, calls `UVC_CMD_CREATE_SEC_CONF`, stores the returned handle, and increments `mm->context.protected_count`. CPU creation allocates per-CPU UV storage plus SIDA, calls `CREATE_SEC_CPU`, and programs SIE PV handles. Page import uses a fault-in callback under `kvm->arch.pv.import_lock`, exports first when required by shared-page ownership rules, rejects large/hugetlb folios, and may request folio splitting. Teardown supports normal destroy, destroy-fast, set-aside async cleanup, and cleanup of pending leftovers on signals or mm release.

## Dependencies And Integration
Depends on Ultravisor UVC ABI, gmap, guest fault-in helpers, Linux MM/MMU notifier, KVM memslots, SIE block PV fields, mm protected-count tracking, usercopy, and KVM lock/SRCU rules.

## Risks And Test Signals
Risks include intentional leaks on impossible UV failures, protected-count imbalance, mm teardown races, set-aside cleanup after fatal signals, folio splitting/retry loops, secure-page ownership transfer, and usercopy length/alignment in dump paths. Signals include protected VM boot/reboot, UV return-code logging, migration/dump tests, mm teardown under process exit, huge-page rejection, and lockdep for documented lock contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/pv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/sigp.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/sigp.c

## Purpose
Handles s390 SIGP interprocessor communication instructions for KVM guests. It emulates common SIGP orders in-kernel, injects KVM local interrupts to target VCPUs, returns architecture condition codes/status words, and delegates reset/start-like orders or configured userspace SIGP handling to userspace.

## Important APIs, Types, And Functions
Public entry points are `kvm_s390_handle_sigp()` and `kvm_s390_handle_sigp_pei()`. Static handlers implement SENSE, external call, emergency and conditional emergency signals, STOP, STOP AND STORE STATUS, SET ARCHITECTURE rejection, SET PREFIX, STORE STATUS AT ADDRESS, SENSE RUNNING, and preparation for START/RESTART/CPU RESET. `handle_sigp_dst()` validates the destination VCPU and dispatches target orders. `handle_sigp_order_in_user_space()` honors `kvm->arch.user_sigp`.

## Control Flow And State
`kvm_s390_handle_sigp()` rejects problem-state execution, decodes source/destination registers and order code, optionally exits to userspace, reads the order parameter, traces the request, then either handles SET ARCHITECTURE locally or routes through `handle_sigp_dst()`. Destination handling refuses most orders while stop/restart IRQs are pending to avoid reporting stale state. Success and status paths set the guest PSW condition code; negative returns propagate kernel or userspace-exit handling. Partial-execution interception only handles external call by waking the target VCPU and accepting the order.

## Dependencies And Integration
Depends on s390 SIGP constants, KVM VCPU lookup, KVM local interrupt injection, stop/restart IRQ state, prefix helpers, guest memory validity checks, tracepoints, and userspace KVM run exits.

## Risks And Test Signals
Risks include incorrect busy/status ordering around asynchronous STOP/RESTART, wrong register half used for parameters, prefix validation/alignment errors, and mismatched userspace delegation counters. Test signals include multi-VCPU guest CPU hotplug/start/stop, external call delivery, SIGP status polling after STOP, userspace SIGP mode, and `kvm_s390_handle_sigp_pei()` wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/sigp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/trace-s390.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/trace-s390.h

## Purpose
Defines tracepoints in the `kvm-s390` trace system for VM/VCPU lifecycle, interrupt injection and delivery, reset requests, channel I/O enablement, IBS/AIS mode changes, suppressed adapter interrupts, and gmap notifier activity.

## Important APIs, Types, And Functions
The file is a trace header using `TRACE_EVENT`. It defines symbolic interrupt-name helpers through `kvm_s390_int_type` and `get_irq_name()`. Events include `kvm_s390_create_vm`, `kvm_s390_create_vcpu`, `kvm_s390_destroy_vcpu`, `kvm_s390_vcpu_start_stop`, `kvm_s390_inject_vm`, `kvm_s390_inject_vcpu`, `kvm_s390_deliver_interrupt`, `kvm_s390_request_resets`, `kvm_s390_stop_request`, `kvm_s390_enable_css`, `kvm_s390_enable_disable_ibs`, `kvm_s390_modify_ais_mode`, `kvm_s390_airq_suppressed`, and `kvm_s390_gmap_notifier`.

## Control Flow And State
Tracepoints are passive instrumentation. Each event defines its prototype, captured fields, fast assignment, and print format. The only state persisted is trace-buffer data emitted by call sites elsewhere in KVM. The file sets `TRACE_SYSTEM` to `kvm-s390` and `TRACE_SYSTEM_VAR` to a valid C identifier, then includes `trace/define_trace.h` outside the include guard.

## Dependencies And Integration
Depends on Linux tracepoint infrastructure and KVM s390 interrupt constants. Integration occurs through generated trace headers included by KVM implementation files and consumed by ftrace/perf/tracefs tooling.

## Risks And Test Signals
Risks are ABI-like trace format churn, incorrect field widths, symbol mapping drift as interrupt constants change, and duplicate trace system definitions. Signals include successful trace header generation, compile coverage, enabling the events under tracefs, and confirming emitted lifecycle/interrupt/gmap messages during KVM test runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/trace-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/trace.h

## Purpose
Defines `kvm` trace-system events specific to s390 VCPU execution, SIE entry/exit, intercepted instructions/program interrupts, SIGP, DIAG, control-register operations, prefix/STAP/STFL/STSI/STHYI, storage-key instructions, and pfault handling.

## Important APIs, Types, And Functions
The file provides common VCPU trace macros (`VCPU_PROTO_COMMON`, `VCPU_FIELD_COMMON`, `VCPU_ASSIGN_COMMON`, `VCPU_TP_PRINTK`) and many `TRACE_EVENT` definitions: `kvm_s390_skey_related_inst`, major pfault init/done events, `kvm_s390_sie_enter`, `kvm_s390_sie_fault`, `kvm_s390_sie_exit`, instruction/program/validity intercepts, `kvm_s390_handle_sigp`, `kvm_s390_handle_sigp_pei`, `kvm_s390_handle_diag`, `kvm_s390_handle_lctl`, `kvm_s390_handle_stctl`, `kvm_s390_handle_prefix`, `kvm_s390_handle_stap`, `kvm_s390_handle_stfl`, `kvm_s390_handle_stsi`, `kvm_s390_handle_operexc`, and `kvm_s390_handle_sthyi`.

## Control Flow And State
This file records diagnostic state only. Events capture VCPU ID plus PSW mask/address, then add event-specific operands such as intercept code, instruction bytes, SIGP order, control-register range, or STSI selectors. It includes s390 decoder metadata to print symbolic instruction/intercept names.

## Dependencies And Integration
Depends on Linux tracepoints, s390 SIE/debug/disassembly headers, and generated symbolic tables for intercepts, SIGP orders, DIAG codes, and instruction decoding. Call sites are in privileged instruction, SIGP, intercept, SIE, and pfault paths.

## Risks And Test Signals
Risks include malformed trace headers, field type mismatches, stale symbolic decoders, and trace output that no longer matches call-site semantics. Test signals are compile-time trace generation, boot with tracing enabled, selective enablement of KVM trace events, and correlation of trace output with KVM guest intercept tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/vsie.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/vsie.c

## Purpose
Implements s390 nested virtualization support through virtual SIE. It shadows a guest-provided SIE control block, constructs or reuses shadow guest address maps, pins referenced guest blocks, runs hardware SIE for guest3 where safe, and forwards/repairs intercepts back to guest2.

## Important APIs, Types, And Functions
The central type is page-sized `struct vsie_page`, containing the shadow SCB, machine-check backup, pointer to the original SCB, satellite block GPAs, cached shadow gmap, shadow CRYCB, and facility list. Public entry points are `kvm_s390_handle_vsie()`, `kvm_s390_vsie_gmap_notifier()`, `kvm_s390_vsie_init()`, `kvm_s390_vsie_destroy()`, and `kvm_s390_vsie_kick()`. Major helpers shadow CPU flags, CRYCB/APCB state, ESA mode, IBC, and SCB fields; map the prefix; pin/unpin SCB and satellite blocks; handle shadow faults, STFLE, MVPG partial execution, and SIE run loops; and manage cached `vsie_page` objects by SCB GPA.

## Control Flow And State
`kvm_s390_handle_vsie()` validates SIEF2, privilege, alignment, and pending host interrupts, obtains a cached or new `vsie_page`, pins the original SCB, shadows allowed state, pins satellite blocks, registers the shadow SCB for kicks, runs `vsie_run()`, unregisters, unpins, unshadows, and releases the page. `vsie_run()` loops over shadow-gmap acquisition, prefix mapping, intervention-request updates, and `do_vsie_run()` until guest2 or host action is needed. Shadow gmaps are cached on the page and invalidated by ASCE/EDAT changes or gmap notifier overlap with the guest prefix.

## Dependencies And Integration
Depends on SIE/SIE block layout, gmap shadow APIs, guest access, KVM SRCU, s390 facilities, crypto/AP masks, lowcore timing and branch-prediction controls, machine-check reinjection, and KVM request/kick behavior.

## Risks And Test Signals
Risks include races on original SCB fields, stale shadow gmaps, prefix mapping invalidation, incomplete state copy-back, wrong intercept forwarding, pinned-block leaks, branch-prediction isolation mistakes, and double-use of an SCB address. Signals include nested KVM boot, MVPG/STFLE nested tests, gmap notifier stress, machine-check reinjection paths, CPU kick/interrupt latency, and lockdep/RCU checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/vsie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/lib/Makefile

## Purpose
Build manifest for s390-specific architecture library objects. It selects low-level helpers for delay, string/memory operations, user access, bit scanning, spinlocks, 128-bit shifts, checksums, probes, and optional architecture sanity tests.

## Important APIs, Types, And Functions
The Makefile adds core library objects through `lib-y` (`delay.o`, `string.o`, `uaccess.o`, `find.o`, `spinlock.o`, `tishift.o`, `csum-partial.o`) and `obj-y` (`mem.o`). Config-gated objects include `probes.o` for KPROBES/UPROBES, KUnit suites for kprobes, unwind, and module relocation sanity tests, `error-inject.o`, and `expoline.o`.

## Control Flow And State
Build-time control flow is purely Kconfig-driven. It disables KASAN instrumentation for `uaccess.o` because user-space access in different address spaces can trigger false positives. `test_kprobes_s390` is composed from assembly and C objects. `test_unwind.o` uses `-fno-optimize-sibling-calls` to preserve call-chain shape for unwinder tests.

## Dependencies And Integration
Integrates with the kernel build system, s390 arch Kconfig, KUnit, KASAN, kprobes/uprobe infrastructure, function error injection, and expoline mitigation configuration.

## Risks And Test Signals
Risks are missing objects under configuration combinations, accidental sanitizer instrumentation of uaccess, or compiler optimization breaking unwind tests. Signals include `allyesconfig`/`allmodconfig` builds, KUnit object linkage, and s390 defconfig builds with combinations of KPROBES, CMM, EXPOLINE_EXTERN, and selftest options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/csum-partial.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/csum-partial.c

## Purpose
Provides s390 implementations of partial internet checksum calculation and unchecked checksum-copy. It uses vector facility instructions when available and falls back to scalar checksum/memcpy support otherwise.

## Important APIs, Types, And Functions
`csum_copy()` is the shared inline engine. It optionally copies from source to destination and accumulates checksum chunks into vector registers. `csum_partial()` computes a checksum over a buffer with an initial sum. `csum_partial_copy_nocheck()` copies while computing the checksum starting from zero. Both public functions are exported.

## Control Flow And State
If VX is unavailable, copy mode performs `memcpy()` and then calls `cksm()`; non-copy mode calls `cksm()` directly. With VX, the function enters kernel FPU context, seeds vector register 16 with the incoming sum, processes 64-, 32-, and 16-byte chunks using vector load/store/checksum operations, handles a tail with vector load/store logical length, folds partial sums into register 16, extracts the sum, and exits FPU context.

## Dependencies And Integration
Depends on s390 checksum and FPU/vector helper APIs, `cpu_has_vx()`, and exported kernel checksum interfaces used by networking and protocol stacks.

## Risks And Test Signals
Risks include FPU context misuse, odd final-fragment length handling, checksum folding mistakes, destination pointer advancement in copy mode, and mismatches between VX and scalar behavior. Signals include network checksum selftests, packet transmit/receive validation, checksum KUnit or lib tests if present, and testing on systems with and without VX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/csum-partial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/delay.c

## Purpose
Implements s390 busy-wait delay primitives used by generic kernel delay APIs.

## Important APIs, Types, And Functions
Exports `__delay()`, `__udelay()`, and `__ndelay()`. `__delay()` executes a simple branch-count loop and explicitly does not promise wall-clock duration. `delay_loop()` waits against the monotonic TOD clock. `__udelay()` and `__ndelay()` convert microseconds/nanoseconds into TOD deltas and call `delay_loop()`.

## Control Flow And State
`__delay()` uses inline assembly `brct` over roughly half the supplied loop count plus one. `delay_loop()` computes an end TOD value and spins with `cpu_relax()` until `tod_after()` reports the current monotonic TOD has passed it. `__ndelay()` uses `do_div()` after scaling to avoid floating point.

## Dependencies And Integration
Depends on s390 TOD clock helpers, `cpu_relax()`, kernel delay exports, and s390 division helper definitions.

## Risks And Test Signals
Risks include overflow in time conversion, assumptions about loops being calibrated, and busy-wait behavior under virtualization. Signals include boot stability, timer/delay selftests, driver behavior requiring short delays, and compile coverage for exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/error-inject.c

## Purpose
Provides the s390 architecture hook used by Linux function error injection to force a probed function to return immediately.

## Important APIs, Types, And Functions
`override_function_with_return(struct pt_regs *regs)` emulates `br 14` by setting the captured PSW address to GPR14, the s390 return address register. It is marked `NOKPROBE_SYMBOL` so kprobes cannot instrument this helper.

## Control Flow And State
The helper mutates only the saved register frame passed by kprobe/error-injection infrastructure. It does not inspect target function state or stack; control flow resumes at the return address when the modified frame is restored.

## Dependencies And Integration
Depends on s390 `pt_regs`, kprobes, and generic `linux/error-injection.h`. It is built only when `CONFIG_FUNCTION_ERROR_INJECTION` is enabled.

## Risks And Test Signals
Risks include wrong return-register assumptions, unsafe probing of the override helper itself, and interactions with nonstandard calling sequences. Signals include function error injection tests, kprobe registration behavior, and fault-injection users that expect immediate function return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/expoline.S -->
# sources/distributed-fs/ceph-client/arch/s390/lib/expoline.S

## Purpose
Generates external branch thunks for expoline/nospec mitigation on s390 when external thunks are configured.

## Important APIs, Types, And Functions
The assembly macro `GEN_ALL_BR_THUNK_EXTERN` iterates registers 1 through 15 and emits `GEN_BR_THUNK_EXTERN %rN` from `asm/nospec-insn.h`.

## Control Flow And State
No runtime state is stored here. The file contributes mitigation thunk symbols at build time so indirect branch sequences can target hardened external thunks.

## Dependencies And Integration
Depends on s390 nospec instruction macros and the build rule gated by `CONFIG_EXPOLINE_EXTERN`. It integrates with compiler/kernel branch mitigation code generation.

## Risks And Test Signals
Risks include missing thunk symbols for a register, mismatch with nospec macro definitions, and build/link failures under expoline configurations. Signals include successful builds with `CONFIG_EXPOLINE_EXTERN`, objdump inspection of thunk symbols, and boot under branch-mitigation settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/expoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/find.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/find.c

## Purpose
Implements s390 MSB0-numbered bit scanning helpers for bitmaps where hardware and architecture conventions number bit 0 at the most significant bit of a word.

## Important APIs, Types, And Functions
Exports `find_first_bit_inv()` and `find_next_bit_inv()`. Both return the first set bit according to inverted/MSB0 numbering and return `size` when no bit is found within bounds.

## Control Flow And State
`find_first_bit_inv()` scans full words until a nonzero word appears, handles a partial tail by masking unused low-order bits, then uses `__fls(tmp) ^ (BITS_PER_LONG - 1)` to convert MSB-position to logical bit index. `find_next_bit_inv()` starts at an offset, masks bits before the offset in the first word, scans middle words, handles a partial final word, and applies the same index conversion.

## Dependencies And Integration
Depends on Linux bitops and export infrastructure. It supports s390 code paths that interact with hardware bitmaps or facility masks with MSB0 numbering.

## Risks And Test Signals
Risks include off-by-one errors for partial words, incorrect masks at nonzero offsets, and returning past `size`. Signals include bitmap unit tests, facility-mask users, and architecture code exercising `test_bit_inv()`/find helpers across boundary sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/mem.S -->
# sources/distributed-fs/ceph-client/arch/s390/lib/mem.S

## Purpose
Provides optimized s390 assembly implementations of core memory operations: `memmove`, `memset`, `memcpy`, and typed memset variants.

## Important APIs, Types, And Functions
Defines and exports `__memmove`/`memmove`, `__memset`/`memset`, `__memcpy`/`memcpy`, `__memset16`, `__memset32`, and `__memset64`. It also emits a branch-return thunk for `%r14` via nospec macros.

## Control Flow And State
`__memmove` chooses forward copy unless destination overlaps the source from above, in which case it copies bytewise in reverse. Forward copy uses 256-byte `mvc` chunks plus an `exrl`-driven remainder. `__memset` specializes zero fill using `xc`, nonzero fill by seeding the first byte then expanding with `mvc`, and handles single-byte cases. `__memcpy` performs forward 256-byte chunks and a remainder. The typed memset macro stores a 16/32/64-bit seed, copies it across 256-byte blocks, and handles remainders.

## Dependencies And Integration
Depends on s390 assembler, `linux/linkage.h`, export macros, and nospec branch macros. These symbols back generic kernel memory APIs on s390.

## Risks And Test Signals
Risks include overlap handling regressions, `exrl` length calculation mistakes, clobber/ABI mismatches, zero-length corner cases, and speculation-thunk changes. Signals include lib/string tests, boot-time memory operations, KASAN/KMSAN reports, compiler built-in replacement tests, and objtool/assembler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/mem.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/probes.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/probes.c

## Purpose
Shared s390 helper logic for kprobes and uprobes instruction validation/fixup.

## Important APIs, Types, And Functions
`probe_is_prohibited_opcode()` rejects unsupported or unsafe instructions such as DIAG, EXECUTE/EXRL, transactional-execution instructions, PSW/program-call instructions, and unknown opcodes. `probe_get_fixup_type()` classifies branch/link/PSW instructions into fixup strategies such as normal PSW advance, return-register fixup, branch-not-taken, or not-required. `probe_is_insn_relative_long()` detects RIL-b/RIL-c long relative instructions that need modification to avoid full emulation.

## Control Flow And State
All logic is stateless table-like opcode decoding over a `u16 *insn` instruction stream. It first validates the instruction with the s390 disassembler, then uses primary opcode and selected extension fields to select behavior.

## Dependencies And Integration
Depends on `asm/kprobes.h`, s390 instruction decoder/disassembler helpers, kprobe fixup constants, and CONFIG_KPROBES/UPROBES build selection.

## Risks And Test Signals
Risks include allowing unsafe opcodes, rejecting valid probe sites, incorrect branch fixup causing wrong resumed PSW, and missing new relative-long opcodes. Signals include kprobe/uprobe selftests, the s390 KUnit kprobes sanity suite, probe registration over branch opcodes, and instruction decoder updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/spinlock.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/spinlock.c

## Purpose
Implements out-of-line s390 spinlock and rwlock wait paths, including queued locking for dedicated CPUs and yield behavior for preempted virtual CPUs.

## Important APIs, Types, And Functions
Exports `arch_spin_lock_wait()`, `arch_spin_trylock_retry()`, `arch_read_lock_wait()`, `arch_write_lock_wait()`, and `arch_spin_relax()`. `arch_spin_lock_setup()` initializes per-CPU queue nodes. Boot/sysctl state is `spin_retry`, configurable via `spin_retry=` and `/proc/sys/kernel/spin_retry`. Internal helpers decode queue tails, issue NIAI-assisted loads/cmpxchg where available, choose yield targets, and implement queued or classic spin acquisition.

## Control Flow And State
Dedicated CPUs use `arch_spin_lock_queued()`: enqueue a per-CPU node into the lock word tail, optionally yield to the owner, wait for predecessor release, acquire the lock with bounded retry/yield loops, then pass queue ownership to the next node. Non-dedicated CPUs use classic spinning with retry-yield loops. RW lock wait paths serialize through an embedded spinlock wait queue and manipulate reader/writer bits in `rw->cnts`.

## Dependencies And Integration
Depends on s390 lowcore, SMP yield APIs, machine type checks, alternatives/NIAI facility 49, sysctl init, and generic arch spinlock types.

## Risks And Test Signals
Risks include queue corruption, incorrect CPU/index encoding, lock stealing fairness bugs, missing memory ordering, interrupt-context read-lock behavior, and virtualization yield heuristics. Signals include lock torture tests, lockdep, SMP stress on LPAR and non-LPAR, sysctl changes, and performance/regression measurements under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/string.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/string.c

## Purpose
Provides optimized s390 C/inline-assembly implementations of string and memory search/compare helpers selected by architecture feature macros.

## Important APIs, Types, And Functions
Conditionally exports `strlen`, `strnlen`, `strcat`, `strlcat`, `strncat`, `strcmp`, `strstr`, `memchr`, `memcmp`, and `memscan`. Internal helpers `__strend()` and `__strnend()` find NUL terminators with `srst`; `clcle()` compares length-bounded byte ranges.

## Control Flow And State
String-end searches loop on s390 string-search instructions until completion. Concatenation finds the destination end, then uses `mvst` or `memcpy` to append. Comparisons use `clst` or `clcle` and translate condition codes into standard C return values. `memchr`/`memscan` search for a byte and return either the match, NULL, or one-past-end depending on API semantics.

## Dependencies And Integration
Depends on architecture string configuration macros, s390 inline assembly condition-code helpers, exported kernel string APIs, and generic `memcpy` from `mem.S` for some append operations.

## Risks And Test Signals
Risks include wrong return semantics for not-found cases, buffer-bound handling in `strlcat`/`strncat`, condition-code translation, and interaction with fortified string wrappers disabled for this implementation. Signals include lib/string tests, fortify build checks, boot/runtime string-heavy workloads, and comparison with generic implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.c

## Purpose
KUnit suite validating s390 kprobe registration rejects invalid offsets inside instructions or odd byte positions while accepting valid function-entry probes.

## Important APIs, Types, And Functions
`setup_kprobe()` initializes a `struct kprobe` by symbol and offset. `test_kprobe_offset()` checks that registration succeeds at offset 0 and fails with `-EINVAL` at a supplied invalid offset. Test cases cover `kprobes_target_odd`, `kprobes_target_in_insn4`, `kprobes_target_in_insn6_lo`, and `kprobes_target_in_insn6_hi`. The suite is named `kprobes_test_s390`.

## Control Flow And State
Each test registers a probe at the target symbol start, unregisters on success, then attempts registration at a problematic offset and expects rejection. The file uses a single static `struct kprobe kp`; tests run through KUnit infrastructure.

## Dependencies And Integration
Depends on KUnit, kprobes, and symbols/offset constants emitted by `test_kprobes_asm.S` and declared in `test_kprobes.h`. Built under `CONFIG_S390_KPROBES_SANITY_TEST`.

## Risks And Test Signals
Risks include target assembly drift invalidating offsets, shared static kprobe state if tests become parallelized, and changed kprobe error codes. The test itself is a signal for instruction-boundary validation and probe decoder correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.h -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.h

## Purpose
Header shared by the s390 kprobes KUnit C test and assembly target file.

## Important APIs, Types, And Functions
Declares four external offset symbols: `kprobes_target_odd_offs`, `kprobes_target_in_insn4_offs`, `kprobes_target_in_insn6_lo_offs`, and `kprobes_target_in_insn6_hi_offs`.

## Control Flow And State
No executable control flow. The declared symbols are data emitted by assembly macros and consumed as invalid offsets by the C KUnit tests.

## Dependencies And Integration
Depends on the companion assembly file for definitions and the C test for use. It is part of the `test_kprobes_s390` composite object.

## Risks And Test Signals
Risks are declaration/definition mismatch or symbol type/width mismatch. Signals are successful linkage of the KUnit test object and runtime kprobes KUnit execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes_asm.S -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes_asm.S

## Purpose
Assembly fixture file for the s390 kprobes KUnit suite. It emits target functions with known invalid probe offsets inside odd bytes or multi-halfword instructions.

## Important APIs, Types, And Functions
Macros `KPROBES_TARGET_START` and `KPROBES_TARGET_END` wrap each target with symbol/function annotations, an ftrace NOP, and an exported offset data symbol. Targets include `kprobes_target_in_insn4`, `kprobes_target_in_insn6_lo`, `kprobes_target_in_insn6_hi`, `kprobes_target_bp`, and `kprobes_target_odd`.

## Control Flow And State
Each target contains hand-encoded instruction halfwords/bytes and returns via `br %r14`. Labels mark intentionally invalid probe positions, and `SYM_DATA(name##_offs, .quad 1b - name)` records the offset from function start.

## Dependencies And Integration
Depends on s390 assembler/linkage macros and ftrace NOP generation. Used with `test_kprobes.c` under the kprobes sanity-test config.

## Risks And Test Signals
Risks include assembler encoding changes, ftrace prologue size assumptions, or offset labels accidentally becoming valid probe sites. Signals are KUnit pass/fail for probe offset validation and successful assembly/linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.c

## Purpose
KUnit test verifying s390 module loading handles a very large number of relocations against vmlinux symbols.

## Important APIs, Types, And Functions
`test_modules_many_vmlinux_relocs()` calls 10,000 generated helper functions through the `REPEAT_10000` macro and asserts that the accumulated result is `49995000`. The KUnit suite is named `modules_test_s390`.

## Control Flow And State
The test initializes `result` to zero, expands 10,000 calls to `test_modules_return_N()`, then compares the sum with the arithmetic-series expected value. There is no persistent runtime state.

## Dependencies And Integration
Depends on KUnit, Linux module support, and generated declarations from `test_modules.h` with definitions/exported symbols in `test_modules_helpers.c`. Built under `CONFIG_S390_MODULES_SANITY_TEST`.

## Risks And Test Signals
Risks include macro expansion size/compile-time cost, mismatch with helper return definitions, and brittle expected-sum assumptions if generated range changes. The test directly signals relocation handling correctness for modules with many vmlinux relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.h -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.h

## Purpose
Macro generator and declarations for the s390 module relocation KUnit test.

## Important APIs, Types, And Functions
Defines nested repetition macros `__REPEAT_10000_1/2/3` and `REPEAT_10000(f)` to expand a macro over numeric suffixes `0000` through `9999`. `DECLARE_RETURN(i)` declares `int test_modules_return_i(void)`, and `REPEAT_10000(DECLARE_RETURN)` emits 10,000 declarations.

## Control Flow And State
No runtime control flow. It creates compile-time repetition to generate a large symbol surface for relocation stress.

## Dependencies And Integration
Used by both `test_modules.c` and `test_modules_helpers.c`. The macro shape must match helper definitions and expected summation in the C test.

## Risks And Test Signals
Risks include accidental numeric token changes, excessive compiler memory/time, or declaration/definition mismatch. Signals are successful compilation/linkage and the KUnit relocation test sum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules_helpers.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules_helpers.c

## Purpose
Defines and exports 10,000 helper functions used to stress s390 module relocation handling.

## Important APIs, Types, And Functions
`DEFINE_RETURN(i)` defines `test_modules_return_i()` returning `1 ## i - 10000` and exports it with `EXPORT_SYMBOL_GPL`. `REPEAT_10000(DEFINE_RETURN)` expands this for every generated suffix.

## Control Flow And State
Each generated function is trivial and stateless. The collective symbol set creates many relocations for the test module.

## Dependencies And Integration
Depends on `test_modules.h` for macro expansion and Linux export infrastructure. Built under `CONFIG_S390_MODULES_SANITY_TEST_HELPERS`, paired with the KUnit test module.

## Risks And Test Signals
Risks include huge object size, token-pasting surprises, export table stress, and expected-value mismatch. Signals include successful module/helper build, symbol exports, and `modules_test_s390` passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_modules_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_unwind.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/test_unwind.c

## Purpose
Large KUnit suite validating s390 stack unwinding across normal calls, explicit stack pointer/regs inputs, alternate stacks, separate tasks, IRQ context, program-check/kprobe/ftrace paths, kretprobe paths, and rethook handling.

## Important APIs, Types, And Functions
`test_unwind()` runs `unwind_for_each_frame()`, formats a backtrace, requires `unwindme_func2` followed by `unwindme_func1`, rejects unwind errors and `arch_rethook_trampoline+0x0`, and can print backtraces via the `backtrace` module parameter. `struct unwindme` carries flags, task state, completion/wait queues, stack pointer, and result. Helpers synthesize regs (`fake_pt_regs()`), install kprobes/kretprobes/ftrace handlers, run timer IRQ tests, spawn kthreads, and form a call chain through `unwindme_func1..4`. `param_list` enumerates many flag combinations and feeds `KUNIT_ARRAY_PARAM`.

## Control Flow And State
Each parameterized test sets `current_test`, initializes flags, then chooses task, IRQ, or direct execution. Direct paths may call into kprobe, kretprobe, ftrace, or fake-regs unwinding. IRQ tests use a timer callback; task tests park a kthread after it reaches a known stack point. Global `unwindme` coordinates asynchronous callback contexts, and `current_test` supports logging.

## Dependencies And Integration
Depends on s390 unwind APIs, KUnit, kallsyms, kthreads, ftrace, timers, kprobes, wait queues, lowcore alternate stack, and module parameters. Built with sibling-call optimization disabled.

## Risks And Test Signals
Risks include fragile symbol-name prefix checks, async global-state races, configuration-dependent skips, ftrace/kprobe cleanup on failure, backtrace buffer truncation, and optimizer effects. The suite itself is a primary signal for unwinder reliability across important s390 contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/test_unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/tishift.S -->
# sources/distributed-fs/ceph-client/arch/s390/lib/tishift.S

## Purpose
Provides s390 assembly implementations of compiler helper functions for shifting 128-bit integers.

## Important APIs, Types, And Functions
Exports `__ashlti3` for arithmetic/logical left shift, `__ashrti3` for arithmetic right shift, and `__lshrti3` for logical right shift. The file lives in `.noinstr.text` and emits a nospec return thunk for `%r14`.

## Control Flow And State
Each helper loads a 128-bit value from the input pointer into `%r0/%r1`, handles zero shift as a direct store, branches between shifts below 64 bits and shifts of 64 or more, combines high/low halves with `ogr` where needed, sign-extends for arithmetic right shifts, stores the result to the output pointer, and returns.

## Dependencies And Integration
Depends on s390 linkage/export/nospec macros and compiler runtime expectations for `__int128` shift helpers. Used when generated kernel code needs 128-bit shifts not inlined by the compiler.

## Risks And Test Signals
Risks include ABI register/pointer convention mistakes, boundary errors at shift counts 0/63/64/127, wrong sign extension, and noinstr constraints. Signals include compiler-generated 128-bit arithmetic tests, boot with configs using `__uint128_t`, and objdump/assembler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/tishift.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/uaccess.c -->
# sources/distributed-fs/ceph-client/arch/s390/lib/uaccess.c

## Purpose
Implements s390 user-address-space compare-and-exchange helpers with storage-key handling, plus an optional debug assertion for user/kernel ASCE state.

## Important APIs, Types, And Functions
Under `CONFIG_DEBUG_ENTRY`, `debug_user_asce()` verifies control registers 1 and 7 match the expected user ASCE on kernel entry/exit. Exported cmpxchg helpers are `__cmpxchg_key1()`, `__cmpxchg_key2()`, `__cmpxchg_key4()`, `__cmpxchg_key8()`, and `__cmpxchg_key16()`. `__cmpxchg_key_small()` implements byte/halfword cmpxchg by aligning to a 32-bit word, masking, and retrying a word `cs`.

## Control Flow And State
All cmpxchg helpers initialize storage-key regions, switch access key with `spka`, execute the appropriate compare-and-swap instruction (`cs`, `csg`, `cdsg`), restore the default key, and use exception-table fixups to return errors and previous values on user access faults. Small sizes loop up to 128 times to handle concurrent modification of unrelated bytes in the containing word, returning `-EAGAIN` if retry budget is exhausted.

## Dependencies And Integration
Depends on uaccess, kprobes annotations, MM/storage-key helpers, control-register access, s390 exception-table macros, and exported architecture atomics used by futex/user-memory paths.

## Risks And Test Signals
Risks include failing to restore access key, exception-table mistakes, byte-order shift/mask errors, livelock or excessive `-EAGAIN`, and faults while in kprobe context. Signals include futex/atomic user access tests, storage-key tests, debug-entry panics, fault-injection on user pages, and KASAN remaining disabled by the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/lib/uaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/mm/Makefile

## Purpose
Build manifest for s390 architecture memory-management code.

## Important APIs, Types, And Functions
Core built-in objects include initialization, fault handling, extmem, mmap, vmem, maccess, page state, page attributes, page tables, page allocation, and exception tables. Optional objects are `cmm.o`, `physaddr.o`, `hugetlbpage.o`, `dump_pagetables.o`, and `pfault.o`. `gmap_helpers.o` is included when `CONFIG_KVM` is set to built-in or module by normalizing module state with `$(subst m,y,$(CONFIG_KVM))`.

## Control Flow And State
Control is entirely build-time and Kconfig-driven. The KVM gmap helper rule ensures architecture memory helpers are available even when KVM is modular.

## Dependencies And Integration
Integrates with the kernel build system, s390 MM subsystem, KVM gmap support, CMM, hugetlb, page-table dump, debug virtual address checking, and pfault.

## Risks And Test Signals
Risks include missing memory-management objects under uncommon configs, wrong KVM module/built-in dependency behavior, and feature objects omitted from s390 builds. Signals include s390 defconfig/allmodconfig builds, KVM module builds, and boot tests for CMM/PFAULT/HUGETLB/PTDUMP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/cmm.c -->
# sources/distributed-fs/ceph-client/arch/s390/mm/cmm.c

## Purpose
Implements s390 Collaborative Memory Management, allowing the guest to voluntarily allocate and donate pages to the hypervisor and later release them, with sysctl and optional IUCV SMSG control.

## Important APIs, Types, And Functions
`struct cmm_page_array` stores donated page addresses in linked page arrays. Global counters/targets track permanent and timed pages plus timeout settings. Core helpers are `cmm_alloc_pages()`, `cmm_free_pages()`, `cmm_oom_notify()`, `cmm_thread()`, `cmm_set_timer()`, `cmm_timer_fn()`, sysctl handlers for `cmm_pages`, `cmm_timed_pages`, and `cmm_timeout`, optional `cmm_smsg_target()`, `cmm_init()`, and `cmm_exit()`.

## Control Flow And State
Initialization registers `/proc/sys/vm` controls, optional SMSG callback, OOM notifier, and the `cmmthread`. The thread sleeps until target counters differ from actual counters, then allocates or frees one page per wake cycle for each class. Allocated pages are passed to the hypervisor with `diag10_range()` and retained in linked arrays under `cmm_lock`. Timed pages are decremented periodically by `cmm_timer_fn()` according to timeout settings. OOM notification frees up to 256 timed pages first, then regular CMM pages, and resets targets to actual counts.

## Dependencies And Integration
Depends on s390 DIAG 10, sysctl, module parameters, kthreads, timers, OOM notifier, page allocator, optional IUCV SMSG, string helpers, and usercopy-like sysctl buffers.

## Risks And Test Signals
Risks include target counters declared `volatile` rather than fully synchronized, sysctl buffer parsing edge cases, timer/thread races during exit, OOM notifier freeing under pressure, page-array metadata allocation failure, and sender authorization for SMSG control. Signals include CMM module load/unload, sysctl read/write behavior, SMSG SHRINK/RELEASE/REUSE commands, OOM stress, timer expiry, and hypervisor memory balloon accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/cmm.c -->
