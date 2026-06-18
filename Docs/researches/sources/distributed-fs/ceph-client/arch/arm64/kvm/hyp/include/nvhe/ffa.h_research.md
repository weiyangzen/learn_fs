# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/ffa.h

## Purpose

This header declares the nVHE FF-A proxy initialization and host-call handling interfaces.

## Important APIs, Types, And Functions

It defines FF-A function-number bounds `FFA_MIN_FUNC_NUM` and `FFA_MAX_FUNC_NUM`, and declares `hyp_ffa_init()` and `kvm_host_ffa_handler()`.

## Control Flow

The implementation initializes proxy pages, then host SMC handling can dispatch FF-A function IDs through `kvm_host_ffa_handler()`.

## State And Persistence Behavior

The header owns no state; implementation state includes proxy page mappings and FF-A mediation data.

## Dependencies And Integration Points

It integrates nVHE host SMC handling, pKVM memory sharing, and FF-A firmware calls.

## Risks And Test Signals

Risks are accepting out-of-range function IDs, bad proxy page ownership, and leaking secure-world shared memory state. Test signals are FF-A init failure/success, host FF-A SMC forwarding, and share/unshare paths with pKVM enabled.
