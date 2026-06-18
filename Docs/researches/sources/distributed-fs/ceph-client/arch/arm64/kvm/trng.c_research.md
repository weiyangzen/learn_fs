<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c

## Purpose
This file implements KVM’s emulation of the ARM SMCCC TRNG service for guests. It answers TRNG version/features/UUID calls and returns host-generated random bits for TRNG RND32/RND64 calls.

## Important APIs, Types, And Functions
- `kvm_trng_call(struct kvm_vcpu *vcpu)` is the external entry point for SMCCC TRNG handling.
- `kvm_trng_do_rnd(struct kvm_vcpu *vcpu, int size)` validates requested bit count, fills a temporary bitmap with `get_random_long()`, clears unused bits, returns up to three result registers, and wipes the temporary buffer.
- Constants define SMCCC TRNG version 1.0, TRNG return codes, maximum returned bits, and the service UUID.

## Control Flow
`kvm_trng_call()` reads the SMCCC function ID from the vCPU. Version returns `0x10000`. Features reports success for supported TRNG functions. UUID returns four little-endian words from the static UUID. RND32 sets `size = 32` and falls through to RND64 handling; both call `kvm_trng_do_rnd()`. Unsupported functions return `TRNG_NOT_SUPPORTED`.

## State And Persistence Behavior
No persistent guest or VM state is stored. Random bits exist in a stack bitmap and are erased with `memzero_explicit()` before return. The only persistent data is the static UUID constant.

## Dependencies And Integration Points
The implementation depends on SMCCC argument/return helpers, KVM vCPU state, the kernel random API, and `kvm/arm_hypercalls.h`. It is reached from KVM hypercall dispatch for SMCCC calls.

## Risks And Edge Cases
- Requests above `3 * size` bits are rejected as `TRNG_INVALID_PARAMETER`.
- The code always reports success for supported RND calls once parameters are valid; it does not currently surface `TRNG_NO_ENTROPY`.
- Return register ordering differs between RND32 and RND64 and must match SMCCC TRNG ABI.
- Temporary entropy must stay wiped even if implementation changes.

## Test Signals
Guest SMCCC tests should query version, features, UUID, valid RND32/RND64 bit counts, and invalid oversized bit counts. Repeated calls should return masked high bits beyond the requested bit count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c -->
