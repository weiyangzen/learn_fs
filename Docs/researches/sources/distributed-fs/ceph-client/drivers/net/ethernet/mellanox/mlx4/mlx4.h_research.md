# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4.h

## Purpose

`mlx4.h` is the private core header for the mlx4 driver. It defines the internal constants, firmware context layouts, command virtualization structures, resource trackers, hardware tables, per-device private state, and cross-file prototypes used by `main.c`, command handling, resource allocators, port code, EQ/CQ/QP/SRQ/MR/UAR code, multicast steering, and multifunction PF/VF support. It is the shared contract for the mlx4 core implementation rather than a public userspace ABI.

## Important APIs, Types, And Functions

Important constants include HCR/communication/clock BAR offsets, MGM entry sizing bounds, command cleanup masks, resource types, allocation modes, QP zone flags, `MGM_QPN_MASK`, `MGM_BLCK_LB_BIT`, VLAN/MAC table sizes, and `MLX4_MAX_NUM_SLAVES`. Firmware-facing packed or endian-aware structures include `mlx4_vhcr`, `mlx4_vhcr_cmd`, `mlx4_mpt_entry`, `mlx4_eq_context`, `mlx4_cq_context`, `mlx4_srq_context`, `mlx4_mgm`, `mlx4_set_port_general_context`, and `mlx4_set_port_rqp_calc_context`.

Core runtime tables include `mlx4_bitmap`, `mlx4_buddy`, `mlx4_icm_table`, `mlx4_uar_table`, `mlx4_mr_table`, `mlx4_cq_table`, `mlx4_eq_table`, `mlx4_srq_table`, `mlx4_qp_table`, and `mlx4_mcg_table`. Multifunction state is modeled by `mlx4_slave_state`, `mlx4_vport_state`, admin/oper VF state arrays, `mlx4_resource_tracker`, `mlx4_mfunc_master_ctx`, and `mlx4_mfunc`. Per-port state is in `mlx4_port_info`, `mlx4_sense`, `mlx4_mac_table`, `mlx4_vlan_table`, and `mlx4_roce_gid_table`. `struct mlx4_priv` embeds the public `struct mlx4_dev` and all private tables, locks, firmware mappings, steering lists, bond map, and work items.

The header declares the internal API surface for bitmap and zone allocation, table init/cleanup, resource wrappers, command setup/cleanup, event dispatch, port sensing, MAC/VLAN/GID operations, resource tracker operations, QP attach/promisc wrappers, MCG sizing helpers, bonding, quotas, and auxiliary-device registration.

## Control Flow Role

This header does not execute control flow directly, but it shapes most mlx4 flows. `main.c` allocates `struct mlx4_priv`, fills `dev->caps`, initializes the table structs declared here, and calls the declared init/cleanup routines in strict order. `mcg.c` uses `mlx4_mcg_table`, `mlx4_mgm`, `mlx4_steer`, and promisc list types to mutate legacy multicast and steering state. Command handling uses `mlx4_cmd`, `mlx4_cmd_info`, VHCR structs, cleanup masks, and wrapper prototypes to route PF and VF commands. Resource tracking uses the enum resource IDs and per-slave lists to reserve, map, and free objects under SR-IOV.

## State And Persistence Behavior

Most structs declared here represent in-kernel runtime state, not persistent storage. Persistent reload state is referenced through `struct mlx4_dev::persist` but the private tables in `mlx4_priv` are rebuilt after reset. Several fields mirror hardware state and must be kept synchronized: ICM table mappings, bitmaps for allocatable objects, MCG and promisc steering lists, MAC/VLAN/GID tables, EQ/CQ/SRQ/QP radix trees, and resource tracker trees. Locking primitives are embedded next to their state: mutexes for port, bond, MCG, MAC/VLAN/GID, command and page-directory paths; spinlocks for bitmap/resource/event fast paths; rwsem/semaphore fields for command execution.

## Dependencies And Integration Points

The header depends on Linux mutex, radix tree, rb tree, timers, semaphores, workqueues, interrupts, spinlocks, rwsems, auxiliary bus, notifier chains, devlink, and public mlx4 device/driver/doorbell/cmd headers. It is included by core implementation files and is tightly coupled to firmware command definitions and public `linux/mlx4/*` device types. Upper mlx4 Ethernet and InfiniBand modules indirectly depend on these declarations through exported core symbols, but external consumers should use public mlx4 headers where possible.

## Risks

Because this header defines shared firmware layouts, structure packing, endianness, and table sizes, small changes can break hardware command ABI. `struct mlx4_priv` is zeroed wholesale by reload code while preserving only selected persistent fields, so adding fields that require special preservation needs explicit lifecycle review. The command wrapper prototype surface is broad; mismatched semantics for wrapped VF commands can cause privilege or resource-accounting bugs. Several arrays are indexed by one-based ports or slave IDs, so bounds assumptions must be maintained consistently. Changes to constants such as MGM entry size, MAC/VLAN table size, or cleanup masks can affect multiple initialization and unwind paths.

## Test Signals

Header changes should be validated by full mlx4 core builds with `CONFIG_MLX4_CORE`, `CONFIG_MLX4_EN`, `CONFIG_MLX4_INFINIBAND`, SR-IOV, DCB, and RFS combinations. Runtime signals include successful PF/VF probe, wrapped command execution, resource allocation/free accounting, port type switching, MCG attach/detach, suspend/resume reload, and AER recovery. Static analysis should check packed firmware structs, endian conversions, array bounds for port/slave indexing, and cleanup coverage for every table declared here.
