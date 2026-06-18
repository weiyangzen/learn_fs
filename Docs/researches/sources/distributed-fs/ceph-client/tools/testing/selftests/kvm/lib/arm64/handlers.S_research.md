# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/handlers.S

## Purpose
This assembly file builds the AArch64 guest exception vector table used by selftests. It preserves guest register state, calls the C exception router, and restores state before returning with `eret`.

## Important APIs, Types, and Functions
Macros `save_registers` and `restore_registers` save x0-x30, an observable SP value, ELR, and SPSR into an `ex_regs`-compatible stack frame. `HANDLER` emits a handler that calls `route_exception(regs, vector)`. `HANDLER_INVALID` emits direct unexpected-exception exits for invalid EL1t vectors. The global `vectors` symbol anchors the vector table.

## Control Flow
The `.entry.text` section is aligned to the architectural 0x800 vector-table boundary. Each 0x80-aligned vector branches to a generated handler. Valid EL1h and EL0 vectors save context, pass vector number to C, then restore context and return.

## State, Dependencies, and Integration
There is no persistent state beyond the stack frame. It integrates with `processor.c` through `route_exception()`, `kvm_exit_unexpected_exception()`, and `vcpu_init_descriptor_tables()`, which writes VBAR_EL1.

## Risks and Test Signals
Register layout must match `struct ex_regs`; any mismatch corrupts handler-visible state. Invalid vectors intentionally exit via ucall, giving tests a clear unexpected-exception failure.
