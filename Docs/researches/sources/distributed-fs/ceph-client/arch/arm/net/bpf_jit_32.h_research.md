# sources/distributed-fs/ceph-client/arch/arm/net/bpf_jit_32.h

## Purpose
Defines the ARM A32 register numbers, condition codes, instruction encodings, and macro constructors used by the 32-bit ARM eBPF JIT emitter.

## Important APIs, Types, And Functions
Defines register constants `ARM_R0` through `ARM_PC`, condition constants `ARM_COND_*`, shift types, base instruction constants such as `ARM_INST_ADD_R`, `ARM_INST_LDR_I`, `ARM_INST_BLX_R`, `ARM_INST_UDF`, and constructor macros such as `ARM_ADD_R`, `ARM_B`, `ARM_LDR_R_SI`, `ARM_MOVW`, `ARM_UMULL`, `ARM_MLS`, and `ARM_UXTH`.

## Control Flow
The file has no runtime flow. Its macros are pure bitfield encoders that assemble ARM instructions from register, immediate, shift, and condition inputs. `ARM_INST_UDF` supplies the faulting fill instruction used for JIT image holes.

## State, Dependencies, And Integration
No persistent state. It is included by `bpf_jit_32.c` and depends on ARM instruction encoding stability. Integration is tight: any macro bug produces invalid JIT machine code.

## Risks And Test Signals
Risks are bitfield mistakes, wrong immediate placement for MOVW/MOVT or load/store forms, UDF conflicts with kernel undefined-instruction hooks, and register-number mismatch with AAPCS expectations. Test signals are BPF JIT selftests, disassembly of `bpf_jit_dump` output, and compile-time coverage of each macro path.
