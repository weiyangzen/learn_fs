
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_book3s.h

## Purpose
Provides a shared symbolic exception-number map for Book3S trace headers. It is included by both PR and HV tracepoint headers to keep exception name formatting consistent.

## Important APIs, Types, And Functions
Defines macro `kvm_trace_symbol_exit`, mapping Book3S exception vectors such as system reset, machine check, data/instruction storage, external, decrementer, syscall, hypervisor storage, emulation assist, performance monitor, AltiVec, and VSX.

## Control Flow
There is no executable control flow. `trace_pr.h` and `trace_hv.h` expand the macro inside `__print_symbolic()` calls for `kvm_exit` or guest exit events.

## State And Persistence
No state is created. The macro contributes static symbolic trace metadata at compile time.

## Dependencies And Integration Points
Integrated with Linux tracepoint formatting. It must be included before the Book3S trace headers use `kvm_trace_symbol_exit`.

## Risks
Missing or stale vector names reduce trace readability and can mislead debugging. Because the macro is shared by PR and HV, edits affect both trace systems.

## Test Signals
Build success for Book3S trace headers and readable ftrace output for Book3S exits are sufficient signals.
