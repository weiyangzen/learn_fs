<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S

## Purpose
`trampoline_common.S` provides the shared zero-IDT descriptor used by real-mode trampolines before entering protected or long mode.

## Important APIs, types, and functions
It exports local `tr_idt`, sized with a 2-byte limit and 8-byte base field to satisfy both 32-bit and 64-bit descriptor-load forms.

## Control flow
Trampoline code includes this file and loads the descriptor before switching modes so unexpected faults shut down rather than vectoring through firmware state.

## State and persistence behavior
No mutable state exists; the descriptor is constant `.rodata`.

## Dependencies and integration points
It depends on `linux/linkage.h`-style symbol macros from the including file context and consumers using `lidt/lidtl` appropriately.

## Risks and edge cases
Wrong descriptor size can corrupt adjacent realmode data or leave a stale IDT active during AP startup.

## Test signals
Signals are AP startup stability and disassembly confirming the IDT descriptor has expected limit/base bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S -->
