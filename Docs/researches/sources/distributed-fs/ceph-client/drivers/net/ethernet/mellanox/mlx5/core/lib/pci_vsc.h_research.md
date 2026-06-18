# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.h

## Purpose
`pci_vsc.h` declares the mlx5 PCI vendor-specific capability gateway API and small enum constants for gateway lock state and scan CR-space selection.

## Important APIs, types, and functions
It defines `enum mlx5_vsc_state` with `MLX5_VSC_UNLOCK` and `MLX5_VSC_LOCK`, defines `MLX5_VSC_SPACE_SCAN_CRSPACE`, declares VSC init, gateway lock/unlock, set-space, fast block-read, and semaphore-space functions, and provides inline `mlx5_vsc_accessible()` to test `dev->vsc_addr`.

## Control flow
The header has no standalone runtime flow. Callers first check accessibility or call APIs that do so, then lock the gateway, select a space, perform reads/writes through implementation functions, and unlock.

## State and persistence behavior
No state is stored here. The inline accessibility check reads the VSC capability offset saved in `struct mlx5_core_dev`.

## Dependencies and integration points
It depends on `struct mlx5_core_dev` being visible through including context. It is used by PCI setup, diagnostic, crash dump, and firmware-control code that needs VSC gateway access.

## Risks and edge cases
Callers must pair lock/unlock and avoid gateway operations when `mlx5_vsc_accessible()` is false. The API exposes only block-read and semaphore-space helpers, so direct write users are intentionally limited to implementation internals.

## Test signals
Build coverage and runtime VSC access tests through `pci_vsc.c` are sufficient. Static analysis should verify all successful locks have matching unlocks.
