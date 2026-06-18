<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h

## Purpose
Provides the OpenRISC SMP interface for CPU identity, CPU discovery, IPI dispatch, and architecture call-function hooks.

## Important APIs, Types, And Functions
`raw_smp_processor_id()` reads `current_thread_info()->cpu`, while `hard_smp_processor_id()` reads `SPR_COREID`. It declares `smp_init_cpus()`, call-function IPI senders, `set_smp_cross_call()`, and `handle_IPI()`.

## Control Flow
Generic SMP code calls these hooks to enumerate CPUs and deliver reschedule or call-function IPIs. The implementation in `kernel/smp.c` wires a platform IPI sender and uses `SPR_COREID` during boot.

## State And Persistence
The header itself has no state. Its declarations operate on CPU masks, per-CPU thread info, and the hardware core ID SPR.

## Dependencies And Integration Points
Depends on `asm/spr.h` and `asm/spr_defs.h`. Integrates Linux SMP core, device-tree CPU nodes, interrupt controller IPI plumbing, and OpenRISC TLB shootdown.

## Risks
Wrong CPU IDs corrupt per-CPU state and TLB shootdown targeting. `set_smp_cross_call()` must be installed before secondary CPU startup.

## Test Signals
SMP boot should mark all DT CPUs possible/present, bring secondaries online, and successfully run `smp_call_function*()` and reschedule IPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h -->
