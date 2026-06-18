# sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.c

## Purpose

`ints.c` provides the common Linux/m68k interrupt controller setup for autovector and user-vector interrupt ranges. It bridges architecture vector-table entries to the generic IRQ subsystem and lets machine code replace default IRQ chips or handlers for specific ranges.

## Important APIs, Types, and Functions

The main APIs are `init_IRQ()`, `m68k_setup_auto_interrupt()`, `m68k_setup_user_interrupt()`, `m68k_setup_irq_controller()`, `m68k_irq_startup_irq()`, `m68k_irq_startup()`, `m68k_irq_shutdown()`, `irq_canonicalize()`, and `handle_badint()`. Two default `irq_chip` instances, `auto_irq_chip` and `user_irq_chip`, use m68k startup/shutdown callbacks. The file references assembler fixup locations `auto_irqhandler_fixup[]` and `user_irqvec_fixup[]`, and the architecture `vectors[]` array.

## Control Flow

`init_IRQ()` assigns `handle_simple_irq` and the default autovector chip to `IRQ_AUTO_1` through `IRQ_AUTO_7`, then delegates board initialization to `mach_init_IRQ()`. Machine code may call `m68k_setup_auto_interrupt()` to patch the autovector handler address and flush the instruction cache. `m68k_setup_user_interrupt()` records the first external vector, assigns default handlers to a contiguous user IRQ range, writes the assembler vector offset fixup, and flushes I-cache. When an IRQ is started, the corresponding vector table entry becomes `auto_inthandler` or `user_inthandler`; shutdown restores `bad_inthandler`.

## State and Persistence Behavior

Persistent state includes `m68k_first_user_vec`, vector-table entries, default IRQ chip associations, and runtime `irq_err_count` increments through `handle_badint()`. The instruction stream is modified through the fixup arrays, making `flush_icache()` required after writes.

## Dependencies and Integration Points

This file depends on `vectors[]`, low-level entry handlers from m68k assembly, generic IRQ APIs, and machine hooks from `<asm/machdep.h>`. Q40 canonicalizes IRQ 11 to 10 for compatibility. `irq.c` provides `do_IRQ()` and the shared `irq_err_count` displayed in `/proc/interrupts`.

## Risks and Edge Cases

Incorrect user-vector base or count can index the vector table incorrectly; the code defends only with `BUG_ON(IRQ_USER + cnt > NR_IRQS)`. Fixup writes without an I-cache flush would keep old branch targets. Starting a user IRQ before `m68k_setup_user_interrupt()` has set `m68k_first_user_vec` can install a handler in the wrong vector slot. `handle_badint()` only warns, so repeated unexpected interrupts can flood logs while continuing to run.

## Test Signals

Build and boot with each platform IRQ controller, inspect `/proc/interrupts` for autovector/user IRQs, request and free IRQs while checking vector entries transition between real handlers and `bad_inthandler`, and confirm Q40 IRQ 11 canonicalizes to 10.
