# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/profile.c

## Purpose
`profile.c` builds the mlx4 HCA context-memory profile from requested resource counts and device capabilities. It sizes QP, CQ, SRQ, MPT, MTT, multicast, completion, and auxiliary context regions, packs them into ICM address space, writes the resulting base/log fields into `struct mlx4_init_hca_param`, and updates `dev->caps` and private tables with the effective resource limits.

## Important APIs, types, and functions
- The exported worker is `mlx4_make_profile()`.
- Resource categories are represented by the local `MLX4_RES_*` enum and `res_name[]` debug names.
- Inputs are `struct mlx4_profile`, `struct mlx4_dev_cap`, and `struct mlx4_init_hca_param`.
- The function updates `dev->caps`, `priv->qp_table.rdmarc_shift`, `priv->qp_table.rdmarc_base`, `priv->mr_table.mpt_base`, and `priv->mr_table.mtt_base`.

## Control flow and integration
The function allocates a temporary array of local `struct mlx4_resource` records. It first scales requested MTT count to cover at least twice system RAM with page-sized entries, capped by mlx4 32-bit device limits. It then loads per-entry sizes from firmware capabilities and requested counts from the profile, rounds each count to a power of two, calculates total byte size, sorts resources by decreasing size, and assigns packed start offsets. If accumulated size exceeds `dev_cap->max_icm_sz`, it fails with `-ENOMEM`.

After packing, it walks the resource records and writes base addresses, log counts, and derived limits into `init_hca` and `dev->caps`. Special cases include system EQ support, RDMARC shift calculation per QP, device-managed multicast steering versus hash/AMGM split, and PD count assignment even though PDs do not consume ICM memory.

## State and persistence behavior
The function persists the selected layout in initialization structures and capability fields used by later table initialization. It does not program hardware directly, but its output defines the firmware HCA initialization command layout and the base offsets used by MR, QP, CQ, EQ, SRQ, and multicast code for the lifetime of the device instance.

## Dependencies
Dependencies include mlx4 firmware capability structures, `mlx4_get_mgm_entry_size()`, steering mode flags, kernel memory sizing via `si_meminfo()`, power-of-two helpers, `MAX_MSIX`, page size, and private mlx4 table state.

## Risks
- MTT auto-scaling depends on system RAM and `log_mtts_per_seg`; overflow or unexpected rounding can request more ICM than firmware allows.
- Resource sorting assumes power-of-two sizes for alignment-friendly packing; changing count/size calculations can introduce gaps or overlaps.
- Several later subsystems trust the generated base/log fields. A wrong profile can break QP, MR, multicast, or EQ table lookup globally.
- System EQ capability handling intentionally uses a sentinel log value; consumers must understand that convention.

## Test signals
Validation should include small and large memory systems, profiles near `max_icm_sz`, device-managed and legacy multicast steering, system EQ and non-system EQ devices, multi-function EQ sizing, and boot/probe checks that all resource table initializers consume the generated caps without overflow.
