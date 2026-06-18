# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/instructions.h

## Purpose
Raw instruction encoding helpers for PowerPC copy/paste and prefixed load/store instructions used when assemblers may not know mnemonics.

## Important APIs, Types, and Functions
Defines `PPC_INST_COPY*`, `PPC_INST_PASTE*`, prefix construction macros, base opcode constants, and convenience macros such as `PLBZ`, `PLD`, `PSTD`, `PLXSD`, `PSTXV0`, and related FP/VSX forms.

## Control Flow
No control flow; macros emit `.long` words through `stringify_in_c` for inline assembly.

## State and Persistence
No state is stored.

## Dependencies and Integration Points
Used by alignment and copy/paste tests to encode architecture-specific instructions independent of toolchain mnemonic support.

## Risks and Test Signals
Risk is incorrect bitfield construction causing SIGILL or testing the wrong instruction. Alignment/copy tests are the signal.
