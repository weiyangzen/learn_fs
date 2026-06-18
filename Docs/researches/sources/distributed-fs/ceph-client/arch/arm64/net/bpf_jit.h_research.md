# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit.h

## Purpose
This header provides compact ARM64 instruction-emission macros for the ARM64 BPF JIT compiler. It wraps generic `aarch64_insn_gen_*()` helpers with BPF-JIT-friendly names for branches, load/store forms, atomics, arithmetic, bitfield operations, logical operations, hints, system register reads, and barriers.

## Important APIs, Types, and Functions
The file defines register aliases such as `A64_R()`, `A64_FP`, `A64_LR`, `A64_ZR`, and `A64_SP`; variant helpers like `A64_VARIANT()` and `A64_SIZE()`; branch macros `A64_CBZ`, `A64_CBNZ`, `A64_B_`, `A64_B`, `A64_BL`, `A64_BR`, `A64_BLR`, and `A64_RET`; load/store macros for register and immediate offsets; pair push/pop macros; exclusive and acquire/release load/store macros; LSE atomic macros; arithmetic and comparison macros; move-wide and bitfield macros; data-processing macros; logical macros; hint macros for PAC, BTI, and NOP; and barrier/system-register macros.

## Control Flow
There is no runtime control flow in the header. Each macro expands to a generated 32-bit ARM64 instruction value, generally by passing the requested registers, sizes, variants, immediates, and operation enum to `<asm/insn.h>` generator functions. Some macros encode ARM64 aliases, such as `MOV` as an ADD or register move depending on SP use, `CMP`/`CMN`/`TST` using zero-register destinations, `MUL` using `MADD` with zero accumulator, and store-only LSE operations using `XZR` as the destination.

## State and Persistence
The header has no state. Its outputs become persistent only when the BPF JIT writes generated instruction words into executable JIT images.

## Dependencies and Integration Points
It depends on `<asm/insn.h>` and its instruction generator API. It is consumed by ARM64 BPF JIT implementation files selected by the adjacent Makefile. The macros encode ARM64 ABI assumptions about register operands, instruction variants, and immediate scaling; branch immediate macros shift BPF-style instruction counts into byte offsets.

## Risks
Incorrect scaling or size variants can generate invalid code or branch to wrong offsets. Atomic memory order macros must match BPF memory semantics. Aliases involving SP and zero register need care because ARM64 encodes SP specially in some instruction classes. If `<asm/insn.h>` generator behavior changes, wrappers may need adjustment.

## Test Signals
BPF JIT selftests, verifier/JIT comparison tests, atomic operation tests, tail-call/branch tests, BTI/PAC-enabled JIT tests, and disassembly inspection of generated programs are useful signals. Build tests with `CONFIG_BPF_JIT=y` ensure all macros used by the compiler still type-check against the instruction generator API.
