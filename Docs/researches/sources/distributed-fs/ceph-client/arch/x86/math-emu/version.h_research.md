# sources/distributed-fs/ceph-client/arch/x86/math-emu/version.h

## Purpose
Carries the software FPU emulator version string.

## Important APIs, Types, And Functions
Defines `FPU_VERSION` as `"wm-FPU-emu version 2.01"`.

## Control Flow
No executable control flow.

## State And Persistence
No mutable state. The macro is compile-time metadata.

## Dependencies And Integration Points
Used wherever the emulator reports or embeds its version.

## Risks
Version drift is the only meaningful risk; the macro may not reflect local changes unless manually maintained.

## Test Signals
Build coverage and any diagnostic output that includes `FPU_VERSION`.
