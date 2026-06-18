# sources/distributed-fs/ceph-client/arch/sparc/kernel/ivec.S

## Purpose
`ivec.S` handles sparc64 interrupt-vector packets received from UPA-style devices. It chains interrupt buckets onto a per-CPU worklist and raises the appropriate soft interrupt level for later C dispatch.

## Important APIs, Types, and Functions
The global function is `do_ivec`, with an internal cross-call path `do_ivec_xcall`. It uses `ivector_table_pa`, `trap_block[].irq_worklist_pa`, `ino_bucket.__irq_chain_pa`, and softint/processor interrupt registers.

## Control Flow and State
The handler extracts the INO from the incoming vector data, handles cross-call vectors specially, computes the physical address of the matching `ino_bucket`, links it at the head of the current CPU's `irq_worklist_pa`, and sets a soft interrupt bit so `handler_irq()` will later drain the list. If the vector is a cross-call, it jumps directly to the cross-call target.

## Persistence and Dependencies
Persistent state is the per-CPU physical worklist and bucket chain pointers. Dependencies include exact `struct ino_bucket` layout from `entry.h`, trap block layout, and IRQ dispatch in `irq_64.c`.

## Integration Points, Risks, and Test Signals
Integration is with hardware interrupt vector traps, SMP cross-calls, and generic IRQ delivery. Risks include bucket-chain corruption, lost interrupts from non-atomic list updates, incorrect physical addressing, and layout drift. Test signals are high-rate device interrupts, SMP cross-calls, correct `/proc/interrupts` increments, and absence of stuck nonzero bucket chains after IRQ handling.
