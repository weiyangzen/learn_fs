# sources/distributed-fs/ceph-client/arch/s390/kvm/intercept.c

## Purpose
Dispatches s390 SIE intercepts to in-kernel handlers or userspace fallback. It handles intercepted instructions, program/external interruptions, stop/validity/wait events, partial execution, selected protected-virtualization notifications, STHYI emulation, and post-instruction PER instruction-fetch processing.

## Important APIs, Types, And Functions
Exported functions are `kvm_s390_get_ilen`, `handle_sthyi`, and `kvm_handle_sie_intercept`. Internal handlers include `handle_stop`, `handle_validity`, `handle_instruction`, `inject_prog_on_prog_intercept`, `handle_itdb`, `should_handle_per_event`, `handle_prog`, `handle_external_interrupt`, `handle_mvpg_pei`, `handle_partial_execution`, `handle_operexc`, `handle_pv_spx`, `handle_pv_sclp`, `handle_pv_uvc`, `handle_pv_notification`, and `should_handle_per_ifetch`.

## Control Flow
`kvm_handle_sie_intercept` rejects ucontrol VMs for in-kernel handling, switches on `icptcode`, updates statistics, and delegates to instruction, program, external interrupt, wait, validity, stop, operation exception, partial execution, key-storage, interrupt-enable, and protected-virtualization handlers. Instruction intercepts dispatch by opcode group to the relevant s390 KVM emulation file, including diagnose handling. Program intercepts optionally process guest-debug PER events, guard against protected-guest specification loops, restore transactional-execution TDB data, and inject a program IRQ with detailed SIE-provided fields. External interrupt intercepts reinject priority-sensitive timer/external-call events or drop to userspace for interrupt loops. Partial MVPG execution faults in source and destination pages then retries the instruction.

Protected-virtualization notifications handle prefix changes, SCLP service interrupt completion, UVC remove-shared-access cleanup, and SIGP fallback. After many instruction-like intercepts, `should_handle_per_ifetch` may invoke `kvm_s390_handle_per_ifetch_icpt` so PER fetch events are delivered even when the instruction is handled by userspace.

## State And Persistence
State changes include vCPU stats, local interrupt state, vCPU stopped state, run exit reasons, reset/debug side effects via delegated handlers, lowcore TDB writes, injected IRQ queues, GPR condition-code/results for STHYI, prefix state for PV SPX, PV secure-page conversion, and SIE block interruption fields. All state is runtime VM/vCPU state.

## Dependencies And Integration Points
Integrates with all s390 KVM instruction handlers, `diag.c`, `gaccess.h` guest memory access, `faultin.h` page fault-in, guest debug PER handling, lowcore access, local/float interrupt injection, protected virtualization UV helpers, STHYI system information, SIGP, wait/stop handling, and KVM userspace exit conventions.

## Risks And Edge Cases
Return codes control whether KVM retries, injects, or exits to userspace; mixing guest exception codes with negative host errors is dangerous. Program-interruption injection must copy SIE fields such as TEID, access IDs, monitor codes, DXC, and PER data exactly. Specification and operation-exception loop avoidance protects host progress. MVPG PEI deliberately faults pages without key checking before retrying. PV notification handlers rely on SIDA data and UV retry semantics. PER fetch processing must be skipped when interrupts or key-storage retries would make an exit misleading.

## Test Signals
Run s390 KVM intercept selftests and guest workloads covering each intercept code, diagnose dispatch, program interruption injection fields, PER filtering/debug exits, stop/store-status, external timer/external-call priority, MVPG partial execution, STHYI, operation-exception userspace fallback, protected-virtualization prefix/SCLP/UVC notifications, and userspace fallback for unsupported intercepts.
