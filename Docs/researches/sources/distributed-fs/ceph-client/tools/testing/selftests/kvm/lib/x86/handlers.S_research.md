<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S

## Purpose
`handlers.S` builds the x86 guest IDT entry stubs used by KVM selftests. Each vector wrapper normalizes the exception frame, saves general-purpose registers, calls C exception routing, restores registers, discards vector/error-code slots, and returns with `iretq`.

## Important APIs, Types, and Functions
The assembly exports `idt_handlers`, an array of stub addresses in `.rodata`, and `idt_handler_code`, the block containing generated wrappers. The shared target `handle_exception` calls the C function `route_exception()` with `%rsp` as a pointer to the saved `struct ex_regs` layout. The `HANDLERS` macro emits stubs for vectors 0 through 255 and accounts for exceptions that already push an error code.

## Control Flow
For vectors without hardware error codes, the stub pushes a synthetic zero. Every stub pushes the vector number and jumps to `handle_exception`. The common handler pushes registers in a fixed order, calls `route_exception`, restores the registers, adjusts the stack by 16 bytes for vector and error code, and executes `iretq`.

## State and Persistence
No persistent data is mutated except for the generated `idt_handlers` address table. Runtime state is the guest stack and register frame during exception dispatch.

## Dependencies and Integration Points
The file integrates with `processor.c`, which installs IDT descriptors pointing at `idt_handlers` and provides `route_exception()`. It depends on x86-64 calling conventions and the expected `struct ex_regs` memory layout.

## Risks and Test Signals
Risks include mismatched stack layout, forgetting synthetic error codes, corrupting callee state, or returning to the wrong RIP/RFLAGS. Test signals are successful guest exception handling, `GUEST_ASSERT` failures with accurate vector metadata, and no unexpected triple faults during selftests that deliberately raise exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S -->
