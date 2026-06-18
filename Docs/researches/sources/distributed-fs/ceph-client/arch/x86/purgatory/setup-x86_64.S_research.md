<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S

## Purpose
Provides the 64-bit purgatory start entry that establishes a known stack/GDT and calls the C purgatory verifier.

## Important APIs, Types, And Functions
Defines `purgatory_start`, local GDT, and local stack. Calls `purgatory` and then jumps to `entry64` for final handoff.

## Control Flow
Entry loads a controlled GDT, switches to a local stack, calls the digest-verification C function, and only if it returns branches to the register-loading `entry64` trampoline.

## State And Persistence
Uses static stack/GDT data inside the purgatory image.

## Dependencies And Integration Points
Depends on `purgatory.c` and `entry64.S`, and serves as the linked entry point selected by the purgatory Makefile.

## Risks And Edge Cases
If the verifier hangs, handoff never occurs by design. The setup code must remain freestanding and relocation-friendly.

## Test Signals
Kexec handoff through purgatory with digest verification and correct final entry state validates the setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S -->
