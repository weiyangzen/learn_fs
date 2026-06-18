# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.c

## Purpose
`pci_vsc.c` implements access to mlx5 PCI vendor-specific capability gateway registers. It finds the VSC capability, serializes gateway access with PCI config locking and a firmware semaphore, switches address spaces, reads blocks through the gateway, and supports semaphore-space locking for firmware/reset coordination.

## Important APIs, types, and functions
Public functions are `mlx5_pci_vsc_init()`, `mlx5_vsc_gw_lock()`, `mlx5_vsc_gw_unlock()`, `mlx5_vsc_gw_set_space()`, `mlx5_vsc_gw_read_block_fast()`, and `mlx5_vsc_sem_set_space()`. Internal helpers handle bit extraction/merge, config dword read/write, flag polling (`mlx5_vsc_wait_on_flag()`), single gateway reads/writes, and fast reads that return the next address.

## Control flow
Initialization is PF-only and records the offset of `PCI_CAP_ID_VNDR` in `dev->vsc_addr`. Gateway locking takes the PCI config access lock, polls the VSC semaphore, reads a counter, writes it back to claim ownership, and verifies the lock value. Unlock writes `MLX5_VSC_UNLOCK` and releases PCI config access. Setting a gateway space writes the target space into the VSC control register, validates status bits, and optionally returns the space size from the address register. Block reads iterate from address zero to requested length using the device-provided next address and periodically call `cond_resched()`.

## State and persistence behavior
The file stores only `dev->vsc_addr` and transient hardware semaphore state. Gateway operations mutate PCI config-space VSC registers and, for semaphore spaces, device firmware semaphore words. There is no disk persistence.

## Dependencies and integration points
It depends on Linux PCI config access APIs, mlx5 logging, `pci_channel_offline()`, and VSC definitions in `pci_vsc.h`. It is initialized from `main.c` after BAR mapping and used by diagnostics, firmware reset, or crash dump paths that need gateway access.

## Risks and edge cases
Failure to unlock after a successful lock can block other gateway users. The retry loops cap at 2048 iterations and may return `-EBUSY` on slow devices. Access is rejected if the VSC capability was not found. Fast block reads return the byte offset reached on failure, not a negative errno, so callers must interpret partial progress correctly. PCI channel offline returns `-EACCES`.

## Test signals
Test PF VSC discovery, non-PF no-op discovery, lock/unlock balance, set-space success and invalid-space failure, block-read partial failure handling, PCI offline behavior, semaphore-space lock/unlock, and long block reads that exercise `cond_resched()`.
