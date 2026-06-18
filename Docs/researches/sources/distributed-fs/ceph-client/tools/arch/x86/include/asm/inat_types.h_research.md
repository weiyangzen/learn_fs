# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/inat_types.h

## Purpose
Provides the primitive types used by the x86 instruction attribute and decoder code.

## APIs, Types, and Functions
Defines `insn_attr_t` as `unsigned int`, `insn_byte_t` as `unsigned char`, and `insn_value_t` as signed int. It has no functions or macros beyond the include guard.

## Control Flow, State, and Persistence
There is no runtime behavior. The selected widths constrain generated attribute table elements, instruction byte storage, and sign-extended decoded values.

## Dependencies and Integration
Included by `inat.h`, then indirectly by `insn.h`, `inat.c`, and `insn.c`. It keeps the tools copy independent of broader kernel typedefs.

## Risks and Test Signals
Risks are ABI drift if table values ever exceed `unsigned int` or decoded immediate/displacement values need a larger signed container. Test signals are clean builds of `inat.c` and `insn.c`, and decoder cases for sign-extended 8/16/32-bit immediates and displacements.
