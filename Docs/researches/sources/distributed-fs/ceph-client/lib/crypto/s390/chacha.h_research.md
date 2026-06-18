# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha.h

## Purpose

This s390 architecture header dispatches generic ChaCha stream encryption to the vector assembly implementation when appropriate. It was read as a complete 36-line file.

## Important APIs, Types, and Functions

It defines `hchacha_block_arch` as the generic HChaCha implementation and implements `chacha_crypt_arch(struct chacha_state *state, u8 *dst, const u8 *src, unsigned int bytes, int nrounds)`.

## Control Flow

The wrapper uses generic ChaCha if the request is one block or less, if `nrounds` is not 20, or if `cpu_has_vx()` is false. Otherwise it enters kernel FPU/vector mode, calls `chacha20_vx`, exits vector mode, and advances `state->x[12]` by the number of rounded-up 64-byte blocks consumed.

## State and Persistence Behavior

The wrapper mutates the caller-owned ChaCha state counter after vector encryption. It uses an on-stack vector/FPU save area and owns no persistent storage.

## Dependencies and Integration Points

It depends on s390 FPU/vector helpers, CPU feature checks, `chacha-s390.h`, and generic ChaCha helpers. It is included by the generic ChaCha library's architecture hook path.

## Risks and Edge Cases

Counter updates must match the assembly's generated keystream count, especially for partial tails. The one-block fallback is intentional because the assembly cannot handle a block or less efficiently/compatibly. Incorrect FPU bracketing would corrupt kernel vector state.

## Test Signals

ChaCha tests around 0, 1, 64, 65, and large byte counts, non-20-round fallback tests, and vector-disabled fallback tests validate this wrapper.
