<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h

## Purpose
`pwrseq.h` defines the internal MMC power-sequence provider contract. It gives provider drivers a common `struct mmc_pwrseq` shape and gives host/core code a stable set of lifecycle helpers.

## Important APIs, Types, And Functions
`struct mmc_pwrseq_ops` contains optional `pre_power_on`, `post_power_on`, `power_off`, and `reset` callbacks. `struct mmc_pwrseq` stores the ops pointer, backing `struct device`, global list node, and owning module. Under `CONFIG_OF`, the header declares provider registration, allocation, dispatch, reset, and free helpers. Without `CONFIG_OF`, registration returns `-ENOSYS`, allocation returns success, and dispatch/free helpers compile to no-ops.

## Control Flow
The header has no active runtime control flow beyond the non-OF inline stubs. The intended flow is provider probe fills `struct mmc_pwrseq` and registers it, host allocation binds by phandle, and the MMC core dispatches callbacks during power transitions.

## State And Persistence
The data structures define persistent in-kernel state: provider identity, callback table, list membership, and module ownership. In non-OF builds, no power-sequence state is persisted because helpers are disabled/stubbed.

## Dependencies And Integration Points
The header depends on Linux list/module/device types through users and on `struct mmc_host`. It is included by the common registry and provider modules. Host code observes only the helper API and does not need to know which provider implements a sequence.

## Risks And Edge Cases
Power sequencing is OF-gated. Non-OF platforms that need special sequencing cannot use this path without additional code. Providers must keep `ops`, `dev`, and `owner` valid for as long as they are registered, and callers must tolerate missing callbacks. Adding a new callback requires coordinated updates to the header, registry dispatchers, and providers.

## Test Signals
Compile tests with and without `CONFIG_OF` verify the stubs and declarations. Runtime tests should show provider binding and callback dispatch only on OF-enabled platforms with a matching `mmc-pwrseq` phandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h -->
