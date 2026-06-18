<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S

## Purpose
Provides a 64-bit entry trampoline that loads a controlled GDT, stack, register set, and jumps to the final kexec kernel entry point.

## Important APIs, Types, And Functions
Defines `entry64`, `entry64_regs`, a local GDT, and a small stack. `entry64_regs` contains slots for all general-purpose registers and final RIP.

## Control Flow
The entry loads the local GDT, sets data segments, switches to the local stack, performs a far return to load CS, loads register values from `entry64_regs`, then jumps through the stored `rip`.

## State And Persistence
`entry64_regs` is patched by kexec setup before execution. The GDT/stack are static purgatory data.

## Dependencies And Integration Points
Used by x86 kexec purgatory and final kernel handoff. Relies on 64-bit flat segment descriptors.

## Risks And Edge Cases
Every register slot must match kexec loader expectations. A bad stack, GDT, or RIP value hangs before the new kernel starts.

## Test Signals
Successful kexec into 64-bit kernels with expected register state validates this trampoline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S -->
