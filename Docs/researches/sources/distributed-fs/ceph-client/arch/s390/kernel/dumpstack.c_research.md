# sources/distributed-fs/ceph-client/arch/s390/kernel/dumpstack.c

## Purpose
Implements s390 stack identification, call-trace printing, register dumping, and fatal oops handling.

## Important APIs, Types, And Functions
Exports `stack_type_name()`, `get_stack_info()`, `show_stack()`, `show_registers()`, `show_regs()`, and `die()`. Internal helpers classify task, irq, nodat, mcck, and restart stacks and print the last breaking-event address.

## Control Flow
Stack classification validates alignment, checks task stack first, then current CPU special stacks, and uses a visit mask to prevent recursive stack walking. Register dumping prints PSW bits, GPRs, disassembled code, optional stack trace, and last breaking-event address. `die()` enters oops handling, stops debug logging, serializes output, notifies die notifiers, prints modules and regs, taints the kernel, and either panics or kills the task.

## State And Persistence
State includes `die_lock` and a static `die_counter`. It reads per-CPU lowcore stack pointers and task stack state. No durable persistence exists.

## Dependencies And Integration Points
Depends on unwind, debug feature, lowcore, disassembler, IPL logging, lockdep, notifier die chain, module printing, and scheduler task death.

## Risks And Edge Cases
Incorrect stack classification can produce misleading traces or loops. Oops path locking must avoid deadlocks. PSW rewind/forward handling must match exception state. Fatal interrupt oops and `panic_on_oops` change termination path.

## Test Signals
Signals include induced kernel oops output, stack unwinder reliability flags, special-stack exception tests, lockdep held-lock output, and panic-on-oops behavior.
