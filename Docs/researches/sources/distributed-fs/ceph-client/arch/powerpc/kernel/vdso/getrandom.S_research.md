# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getrandom.S

## Purpose
Provides the assembly vDSO wrapper for `__kernel_getrandom`, bridging PowerPC ABI details to the generic C vDSO getrandom implementation.

## Important APIs, Types, And Functions
Exports `__kernel_getrandom(buffer, len, flags, opaque_state, opaque_len)`. The `cvdso_call` macro builds caller and callee stack frames, saves LR and on 64-bit TOC `r2`, calls `__c_kernel_getrandom`, and converts negative errors to syscall-style return with SO set.

## Control Flow
The wrapper creates two minimum stack frames because vDSO callers are not required to have one, calls the C helper, restores LR/TOC, tears down both frames, returns nonnegative results directly, and returns positive errno with SO set for failures.

## State And Persistence
No private state. It reads/writes caller-provided buffer and opaque getrandom state through the C helper.

## Dependencies And Integration Points
Depends on the generic vDSO random implementation included by the Makefile, PowerPC ABI stack/TOC conventions, and `vgetrandom-chacha.S` for the architecture ChaCha20 block primitive.

## Risks And Edge Cases
Stack-frame correctness is ABI-critical, especially for callers without frames and 64-bit TOC preservation. Error conversion must match libc expectations for vDSO calls. The routine assumes the C helper handles validation and fallback.

## Test Signals
Run getrandom vDSO selftests for success, unsupported flags, short buffers, opaque state handling, signal safety, 32-bit and 64-bit ABIs, and forced fallback paths.
