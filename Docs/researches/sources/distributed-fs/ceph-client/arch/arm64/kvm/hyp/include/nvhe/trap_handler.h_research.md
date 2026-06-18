# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trap_handler.h

## Purpose

This header declares nVHE host trap-handling entry points for exceptions taken from the host into protected hyp.

## Important APIs, Types, And Functions

It declares `handle_trap()` and `handle_host_mem_abort()`.

## Control Flow

The implementation dispatches host traps, including memory aborts, based on the host CPU context and ESR/FAR state.

## State And Persistence Behavior

The header owns no state; implementations mutate host context, host stage-2 mappings, and injected host exceptions.

## Dependencies And Integration Points

It integrates with nVHE hyp-main trap dispatch and pKVM memory protection.

## Risks And Test Signals

Risks are misrouting host faults, failing to inject host exceptions, or corrupting host context. Test signals are protected-mode host memory aborts, host SMC/HVC traps, and pKVM permission faults.
