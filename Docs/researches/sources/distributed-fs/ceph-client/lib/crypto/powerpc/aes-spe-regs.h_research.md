# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-regs.h

## Purpose
Defines common register aliases for the PowerPC SPE AES implementation. It lets AES mode and core assembly share a stable argument and scratch-register vocabulary.

## Important APIs, Types, and Functions
There are no functions or C types. The file maps logical names such as `rDP`, `rSP`, `rKP`, `rRR`, `rLN`, `rIP`, `rKT`, `rD0` through `rD3`, `rW0` through `rW7`, `rI0` through `rI3`, and `rG0` through `rG3` to PowerPC registers.

## Control Flow
This header has no runtime control flow. It affects code generation by macro substitution in assembly sources that include it.

## State and Persistence
No state is stored. Its aliases document which registers carry source/destination pointers, key schedule pointers, round counts, lengths, IVs, tweaks, and scratch data while the including assembly runs.

## Dependencies and Integration Points
Included by `aes-spe-modes.S` and expected to be consistent with the low-level AES core assembly calling convention. The aliases also reflect Linux PowerPC ABI requirements around volatile and nonvolatile registers that the including files save/restore.

## Risks
Register alias drift would silently break assembly call contracts. `rKT` and `rD0` both alias `r9` in different contexts, so maintainers must preserve the existing phase separation between tweak-key argument use and data-register use.

## Test Signals
Any AES SPE mode known-answer failure can indicate register contract breakage. Assembly build failures or objdump review of function prologues are useful after edits to this header.
