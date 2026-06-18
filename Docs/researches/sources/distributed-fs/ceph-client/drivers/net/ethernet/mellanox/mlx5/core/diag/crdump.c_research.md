# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/crdump.c

## Purpose

`crdump.c` provides collection and enablement for mlx5 protected CR-space dumps through the PCI VSC gateway. It is used by health/debug paths to snapshot device control-register space when supported.

## Important APIs, Types, and Functions

- `mlx5_crdump_enable()` probes PF-only VSC access, selects scan CR-space, reads its size, and stores it in `dev->priv.health.crdump_size`.
- `mlx5_crdump_disable()` clears the stored dump size.
- `mlx5_crdump_collect()` locks the VSC gateway, takes the SW-reset semaphore, selects CR-space scan space, and fills caller-provided memory.
- `mlx5_crdump_fill()` initializes the buffer with `BAD_ACCESS`, reads the dump block, and verifies the full expected size was read.

## Control Flow

Enablement is a capability probe: non-PF, inaccessible VSC, already-enabled, or unsupported scan space all return success with no dump enabled. Collection refuses if disabled, then serializes access with `mlx5_vsc_gw_lock()` and `MLX5_SEMAPHORE_SW_RESET`. It always releases the semaphore and gateway lock on exit after a successful acquisition.

## State and Persistence Behavior

The only persistent state is `dev->priv.health.crdump_size`. Dump data is written into caller memory. The file temporarily changes VSC gateway space and semaphore state during collection.

## Dependencies and Integration Points

Depends on `lib/pci_vsc.h`, `lib/mlx5.h`, mlx5 health state, and VSC gateway/semaphore helpers. It integrates with health reporters or crash diagnostics that allocate dump buffers.

## Risks and Edge Cases

- Unsupported CR-space scanning is intentionally masked during enablement, so absence of dumps may be silent.
- `mlx5_crdump_collect()` relies on the caller to pass a buffer large enough for `crdump_size`.
- If another PF is resetting or dumping, collection returns busy or semaphore errors.
- Partial VSC reads return `-EINVAL` after logging how much was read.

## Test Signals

Run on PF hardware with VSC access and verify enablement sets a nonzero dump size. Exercise concurrent dump/reset attempts to verify semaphore handling. Fault-inject short reads and gateway lock failures.
