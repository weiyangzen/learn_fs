# sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.c

## Purpose

`traps.c` implements m68k exception and bus-error handling, CPU-specific page-fault decoding, 68040 writeback cleanup, diagnostic stack/register dumps, signal mapping for user traps, and fatal kernel trap handling.

## Important APIs, Types, and Functions

Externally visible functions include `buserr_c()`, `berr_040cleanup()`, `trap_c()`, `die_if_kernel()`, `set_esp0()`, `fpsp040_die()`, and optional `fpemu_signal()`. Important CPU-specific helpers are `access_error060()`, `probe040()`, `do_040writeback1()`, `do_040writebacks()`, `access_error040()`, `bus_error030()` or Sun3 variant, and `access_errorcf()` for ColdFire MMU. Diagnostic helpers include `show_registers()`, `show_stack()`, and `show_trace()`.

## Control Flow

`buserr_c()` records `esp0` for user frames, decodes ColdFire fault-status bits when applicable, then dispatches by exception frame format: 060 access error, 040 access error, 020/030 bus error, or fatal unknown format. Each CPU path computes fault address and error code, calls `do_page_fault()` when the fault is a recoverable mapping/protection event, or sends SIGBUS/SIGSEGV/SIGKILL and logs diagnostics for unrecoverable cases. 040 handling additionally processes pending writeback slots and can defer cleanup through signal delivery.

`trap_c()` handles non-bus traps. Supervisor traps try `fixup_exception()` on MMU builds, otherwise call `bad_super_trap()` and die. User traps map vectors to `SIGILL`, `SIGFPE`, `SIGBUS`, or `SIGTRAP` with detailed `si_code` and fault address selection based on frame format.

## State and Persistence Behavior

The code mutates current thread fault fields (`signo`, `faddr`, `esp0`), sends signals, performs TLB/cache operations, can rewrite 040 writeback frame slots, taints the kernel on fatal traps, and terminates tasks. It does not persist external data.

## Dependencies and Integration Points

It depends on `struct frame` layout, CPU/MMU feature macros, `do_page_fault()`, exception tables, TLB/cache helpers, signal APIs, FPU emulator/FPSP code, and entry assembly that calls `buserr_c()`/`trap_c()`. `traps.h` exposes functions used from assembly and signal code.

## Risks and Edge Cases

Exception frame formats are CPU-specific and dense. Wrong fault-address/error-code decoding can turn a recoverable page fault into a process kill or kernel oops. 040 writeback cleanup is subtle because user-space fault recovery and kernel exception fixups interact. Diagnostic code reads around PC and stack with no-fault helpers, but invalid frames can still reduce clarity.

## Test Signals

Page-fault tests for read/write/protection/COW, illegal instruction, divide by zero, breakpoint, single-step, kernel exception-table fixups, 040 writeback fault cases, 060 branch prediction/access errors, ColdFire TLB misses, and Sun3 demand mapping are the key signals.
