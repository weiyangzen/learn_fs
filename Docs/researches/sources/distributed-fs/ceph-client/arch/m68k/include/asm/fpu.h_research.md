<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h

## Purpose
`fpu.h` provides the architecture constant for the maximum saved floating-point state size used by task switching, signal frames, and the m68k FPU emulator.

## Important APIs, Types, and Functions
The only API is `FPSTATESIZE`. It is selected by CPU/FPU configuration: 216 bytes for 68020/68030, 96 for 68040, 28 for the emulator, 16 for ColdFire MMU, 12 for 68060, and zero when no supported FPU state exists.

## Control Flow, State, and Persistence
There is no runtime control flow or state. The preprocessor computes the ABI-visible constant at build time.

## Dependencies and Integration Points
The header integrates with thread state layout and the math emulator. `math-emu.h` explicitly warns that changes to the C FPU data layout must stay in sync with the size defined here.

## Risks
Wrong values break context-save sizing and can corrupt adjacent task state. The configuration order matters: emulator and ColdFire choices are mutually exclusive with classic FPU CPU choices in normal builds.

## Test Signals
Compile coverage across 020/030, 040, 060, ColdFire MMU, and emulator configs is the key signal. Runtime signals include stable FPU context switching, signal delivery, and emulator tests under `CONFIG_M68KFPU_EMU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h -->
