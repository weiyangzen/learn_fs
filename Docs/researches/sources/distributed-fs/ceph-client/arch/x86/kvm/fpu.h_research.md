# sources/distributed-fs/ceph-client/arch/x86/kvm/fpu.h

## Purpose

`fpu.h` provides inline helpers for KVM's x86 emulator to read and write live guest FPU/SIMD registers. It defines vector types, lane conversion macros, raw inline-assembly accessors for XMM/YMM/MM registers, and wrappers that lock and load kernel FPU state before direct register access.

## Important APIs, Types, And Functions

- `sse128_t` and `avx256_t`: 128-bit and 256-bit vector types.
- `sse128_lo()`, `sse128_hi()`, `sse128_l0()` through `sse128_l3()`, and `sse128(lo, hi)`: lane extraction/construction helpers.
- Raw helpers: `_kvm_read_avx_reg()`, `_kvm_write_avx_reg()`, `_kvm_read_sse_reg()`, `_kvm_write_sse_reg()`, `_kvm_read_mmx_reg()`, `_kvm_write_mmx_reg()`.
- Locking helpers: `kvm_fpu_get()` and `kvm_fpu_put()`.
- Public wrappers: `kvm_read_avx_reg()`, `kvm_write_avx_reg()`, `kvm_read_sse_reg()`, `kvm_write_sse_reg()`, `kvm_read_mmx_reg()`, `kvm_write_mmx_reg()`.

## Control Flow

Each public helper locks FPU state with `kvm_fpu_get()`, performs one raw register move selected by register number, and unlocks with `kvm_fpu_put()`. `kvm_fpu_get()` calls `fpregs_lock()`, asserts state consistency, and forces a lazy FPU load through `switch_fpu_return()` when `TIF_NEED_FPU_LOAD` is set.

Raw helpers use `vmovdqa` for YMM, `movdqa` for XMM, and `movq` for MMX. Registers 8-15 are available only under `CONFIG_X86_64`; invalid indices call `BUG()`.

## State And Persistence

The helpers access live CPU FPU registers and do not allocate persistent storage. Persistence belongs to surrounding KVM FPU/vCPU state management that has loaded guest registers before emulator access. The critical state rule is that all direct register access must occur while FPU registers are locked and loaded.

## Dependencies And Integration Points

The header depends on `<asm/fpu/api.h>` and x86 inline assembly. `emulate.c` uses it for SIMD/MMX operands and for FPU-state instructions that must run under the same locking model.

## Risks And Maintenance Notes

- Architectural CR0/CR4/XCR0 checks are the caller's responsibility.
- Decode must not pass invalid register numbers, because the helpers call `BUG()`.
- High XMM/YMM registers are 64-bit-build only.
- Kernel FPU API changes require auditing `kvm_fpu_get()` and all direct register users.

## Test Signals

Test SSE/AVX/MMX register moves, XMM/YMM 8-15 on 64-bit builds, CR0.TS/EM and CR4/XCR0 gating in the emulator, lockdep around FPU access, and 32-bit/64-bit build coverage.
