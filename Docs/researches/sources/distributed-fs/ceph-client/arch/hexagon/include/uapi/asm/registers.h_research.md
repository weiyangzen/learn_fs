# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/registers.h

## Purpose

`registers.h` defines the user-visible Hexagon trap register frame ABI. It models `struct hvm_event_record` and `struct pt_regs`, names the GPR, loop, predicate, HVME, syscall, and restart fields saved on exception entry, and supplies accessor macros such as `pt_elr`, `pt_cause`, `pt_badva`, `pt_psp`, `pt_set_singlestep`, `pt_set_kmode`, and `pt_set_usermode`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The important API is the exact field layout consumed by signal delivery, ptrace, KGDB, traps, syscall restart, and assembly entry/exit code. The macros hide the HVME subrecord layout and encode the difference between kernel and user return state. Concrete declarations observed in the file: Macros: `_ASM_REGISTERS_H`, `pt_elr`, `pt_set_elr`, `pt_cause`, `user_mode`, `ints_enabled`, `pt_psp`, `pt_badva`, `pt_set_singlestep`, `pt_clr_singlestep`, `pt_set_rte_sp`, `pt_set_kmode`, `pt_set_usermode`. Types referenced or declared: `hvm_event_record`, `pt_regs`.

## Control Flow, State, And Persistence

There is no executable flow; state is the saved register image placed on the kernel stack by `vm_entry.S` and then inspected or rewritten by C handlers before `restore_pt_regs` returns to user or kernel context.

## Dependencies And Integration Points

It integrates with `asm/ptrace.h`, `kernel/signal.c`, `kernel/traps.c`, `kernel/process.c`, `kernel/kgdb.c`, `kernel/ptrace.c`, and generated asm offsets. Layout changes must stay synchronized with assembly offsets and the UAPI signal/ptrace ABI.

## Risks And Test Signals

Risks are ABI breakage, incorrect user/kernel mode detection, bad single-step state, or mismatched stack pointer restoration. Test signals are Hexagon build coverage, ptrace register get/set, signal round trips, syscall restart tests, KGDB register dumps, and boot through exception entry/exit paths.
 A local static signal for this file is that it has 230 lines and 4623 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
