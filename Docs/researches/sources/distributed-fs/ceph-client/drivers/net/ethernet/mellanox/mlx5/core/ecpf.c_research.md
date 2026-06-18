# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.c

## Purpose

`ecpf.c` handles embedded CPU PF (ECPF) host-PF administration. It detects embedded CPU state, enables/disables the external host PF HCA when the ECPF is responsible, and waits for host PF/VF firmware pages to be reclaimed during cleanup.

## Important APIs, Types, and Functions

- `mlx5_read_embedded_cpu()` reads the initialization segment bit `MLX5_ECPU_BIT_NUM`.
- `mlx5_cmd_host_pf_enable_hca()` / `mlx5_cmd_host_pf_disable_hca()` send `ENABLE_HCA` and `DISABLE_HCA` commands for function ID 0 with `embedded_cpu_function=0`.
- `mlx5_ec_init()` initializes ECPF host-PF administration.
- `mlx5_ec_cleanup()` disables host PF administration and waits for host PF/VF page counters.
- Local `mlx5_host_pf_init()` / `mlx5_host_pf_cleanup()` call eswitch host-PF HCA helpers unless eswitch-manager mode owns that lifecycle.

## Control Flow

If the core device is not an ECPF, init and cleanup are no-ops. For ECPF devices, init enables the external host PF HCA unless eswitch manager mode will do so after eswitch setup. Cleanup reverses the operation, then waits for firmware pages attributed to `MLX5_HOST_PF` and `MLX5_VF`.

## State and Persistence Behavior

The file changes firmware HCA enable state for the host PF and observes page counters in `dev->priv.page_counters`. It does not allocate local persistent state.

## Dependencies and Integration Points

Depends on eswitch support, mlx5 command execution, core role helpers, firmware page wait helpers, and `ecpf.h`. It integrates with core device init/cleanup and eswitch host-PF management.

## Risks and Edge Cases

- Cleanup logs but does not fail on host PF disable errors or page reclaim timeouts.
- Eswitch-manager mode changes who enables/disables the host PF; lifecycle ordering with eswitch setup/teardown is critical.
- The host PF command uses function ID 0, so changes to function numbering assumptions would be high impact.

## Test Signals

Boot ECPF hardware in separate host mode and eswitch-manager mode. Verify host PF HCA enable/disable commands and page reclaim waits. Test cleanup while host PF/VFs still hold pages.
