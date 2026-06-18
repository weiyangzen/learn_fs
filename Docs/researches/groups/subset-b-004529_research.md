# subset-b-004529 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mr.c

## Purpose
`mr.c` implements mlx4 memory translation resources: memory translation table (MTT) range allocation, memory protection table (MPT) reservation and hardware enablement, memory region (MR) and memory window (MW) lifecycle, and translation-page writes. It is the core resource manager used by upper mlx4 Ethernet and RDMA consumers before queue pairs can DMA into registered buffers.

## Important APIs, types, and functions
- MTT allocation uses the private `struct mlx4_buddy` allocator through `mlx4_buddy_alloc()`, `mlx4_buddy_free()`, `mlx4_buddy_init()`, and `mlx4_buddy_cleanup()`.
- Public MTT APIs include `mlx4_mtt_init()`, `mlx4_mtt_cleanup()`, `mlx4_mtt_addr()`, `mlx4_write_mtt()`, and `mlx4_buf_write_mtt()`.
- MPT/MR hardware transitions use `mlx4_SW2HW_MPT()`, `mlx4_HW2SW_MPT()`, `mlx4_mr_hw_get_mpt()`, `mlx4_mr_hw_write_mpt()`, `mlx4_mr_hw_put_mpt()`, `mlx4_mr_hw_change_pd()`, and `mlx4_mr_hw_change_access()`.
- MR lifecycle is handled by `mlx4_mr_alloc()`, `mlx4_mr_free()`, `mlx4_mr_rereg_mem_write()`, `mlx4_mr_rereg_mem_cleanup()`, and `mlx4_mr_enable()`.
- MW lifecycle is handled by `mlx4_mw_alloc()`, `mlx4_mw_enable()`, and `mlx4_mw_free()`.
- Table setup and teardown are `mlx4_init_mr_table()`, `mlx4_cleanup_mr_table()`, and `mlx4_SYNC_TPT()`.

## Control flow and integration
Normal MR creation reserves an MPT index with `mlx4_mpt_reserve()`, initializes an MTT range with `mlx4_mtt_init()`, writes page translations through `mlx4_write_mtt()` or `mlx4_buf_write_mtt()`, and then enables the MR with `mlx4_mr_enable()`. Enablement maps ICM for the MPT entry, fills a command mailbox with the key, PD, access flags, IOVA, size, page shift, and MTT address, then issues `MLX4_CMD_SW2HW_MPT`. Freeing reverses the state: if the entry is hardware-owned it is moved back with `HW2SW_MPT`, MTTs are released, ICM is unmapped, and the MPT bitmap entry is freed.

The file has native and multi-function paths. Native functions directly manage `priv->mr_table` bitmaps, ICM tables, and DMA-visible MTT entries. Multi-function devices forward reserve, map, free, query, and write operations to the master through wrapped mlx4 resource commands such as `RES_MTT`, `RES_MPT`, `RES_OP_RESERVE`, `RES_OP_MAP_ICM`, and `MLX4_CMD_WRITE_MTT`.

## State and persistence behavior
Runtime state lives in `mlx4_priv(dev)->mr_table`, especially `mpt_bitmap`, `mtt_buddy`, `dmpt_table`, and `mtt_table`. Each `struct mlx4_mr` persists its key, PD, IOVA, size, access flags, enabled state, and embedded `struct mlx4_mtt`. MTT entries are DMA-visible hardware state and are explicitly synchronized for CPU and device access when written in native mode. MPT entries transition between software-owned and hardware-owned states; errors in this transition leave resources reserved but not usable until cleanup.

## Dependencies
The implementation depends on mlx4 command helpers, mailbox allocation, ICM table mapping, bitmap allocation, DMA synchronization, endian conversion, kernel spinlocks, vmalloc-backed bitmaps, and capability values from `dev->caps`. It is integrated with RDMA core users through exported GPL symbols and with virtualization through wrapped command opcodes.

## Risks
- The buddy allocator assumes power-of-two table geometry; wrong `num_mtts` or `log_mtts_per_seg` values can corrupt range accounting.
- MR re-registration must clean up replacement MTTs on failure or stale translation state can leak.
- `mlx4_mr_hw_get_mpt()` requires external serialization; concurrent callers can race `HW2SW_MPT` and mailbox ownership.
- Native MPT writes rely on memory barriers and `mlx4_SYNC_TPT()`. Missing ordering would expose partially initialized entries to hardware.
- Multi-function error paths log failed releases but cannot force master cleanup, so leaked reserved MPT/MTT resources are possible after command failures.

## Test signals
Useful validation includes MR/MW allocation and free stress, zero-page physical MRs, fast-register MRs with `page_shift == 0`, reregistration with changed IOVA and size, MTT writes crossing page boundaries, slave and master resource command paths, injected mailbox allocation failures, injected `SW2HW_MPT`/`HW2SW_MPT` failures, and teardown checks for bitmap/ICM leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/pd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/pd.c

## Purpose
`pd.c` manages protection domains, XRC domains, user access regions (UARs), and BlueFlame doorbell mappings for mlx4. These resources are the low-level handles that RDMA and Ethernet queues use to isolate memory access, map doorbell pages, and obtain write-combining BlueFlame registers.

## Important APIs, types, and functions
- PD allocation is exposed by `mlx4_pd_alloc()` and `mlx4_pd_free()`.
- XRC domain allocation uses `__mlx4_xrcd_alloc()`, `mlx4_xrcd_alloc()`, `__mlx4_xrcd_free()`, and `mlx4_xrcd_free()`.
- Table setup and teardown are `mlx4_init_pd_table()`, `mlx4_cleanup_pd_table()`, `mlx4_init_xrcd_table()`, and `mlx4_cleanup_xrcd_table()`.
- UAR handling is `mlx4_uar_alloc()`, `mlx4_uar_free()`, `mlx4_init_uar_table()`, and `mlx4_cleanup_uar_table()`.
- BlueFlame allocation and release are `mlx4_bf_alloc()` and `mlx4_bf_free()`.
- Important state types include `struct mlx4_uar`, `struct mlx4_bf`, `priv->pd_bitmap`, `priv->xrcd_bitmap`, `priv->uar_table.bitmap`, `priv->bf_list`, `priv->bf_mutex`, and `priv->bf_mapping`.

## Control flow and integration
PD and native XRC allocation are direct bitmap operations. Multi-function XRC allocation is delegated to the master with wrapped `RES_XRCD` commands. UAR allocation reserves a UAR bitmap index, converts it to a BAR2 page frame number, and handles slave devices by folding the index into the visible BAR size.

BlueFlame allocation first reuses a partially free UAR from `priv->bf_list`. If none exists, it preserves a firmware-reserved UAR margin, allocates a new `struct mlx4_uar`, reserves a UAR, maps the regular page with `ioremap()`, maps the write-combining BlueFlame page through `io_mapping_map_wc()`, and then hands out one register slice by setting a bit in `free_bf_bmap`. Freeing clears that bit, returns non-full UARs to the list, and fully unmaps/frees the UAR when the last BlueFlame slice is released.

## State and persistence behavior
The file owns in-memory bitmap state for PDs, XRCDs, and UARs. `struct mlx4_uar` stores the allocated index, PFN, normal mapping, write-combining mapping, BlueFlame free-bit map, and list linkage. `struct mlx4_bf` stores the selected UAR, register pointer, offset, and buffer size. There is no disk persistence, but BAR mappings and write-combining mappings persist until explicit free or driver teardown.

## Dependencies
This code depends on mlx4 bitmap helpers, PCI BAR resources, `dev->caps` sizing fields, `mlx4_get_num_reserved_uar()`, Linux `ioremap()`/`iounmap()`, `io_mapping_map_wc()`/`io_mapping_unmap()`, mutexes, and multi-function command wrappers.

## Risks
- BlueFlame allocation must keep `priv->bf_list` and `free_bf_bmap` consistent under `bf_mutex`; a missed list update can hide or double-allocate a register slice.
- Error labels in the UAR mapping path must unmap and free in exact reverse order.
- Slave UAR PFN folding depends on BAR2 size and `uar_page_size`; wrong sizing maps the wrong doorbell page.
- The reserved UAR threshold protects firmware/internal use; relaxing it can starve reserved pages.
- XRC and UAR release failures in multi-function mode are only logged, leaving cleanup dependent on the master.

## Test signals
Tests should cover PD/XRCD bitmap exhaustion and reuse, UAR allocation on master and slave devices, BlueFlame allocation until a page is full, freeing slices in different orders, injected map failures at `ioremap()` and `io_mapping_map_wc()`, and module teardown with no leaked UAR mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/port.c

## Purpose
`port.c` is the mlx4 port resource and configuration layer. It manages per-port MAC tables, VLAN tables, RoCE GID tables, multi-function bonding mirrors, SET_PORT command filtering and rewriting, InfiniBand port capability aggregation, Ethernet port attributes, multicast/VLAN/stat wrappers, transceiver EEPROM reads, and traffic-class reporting.

## Important APIs, types, and functions
- Table initialization: `mlx4_init_mac_table()`, `mlx4_init_vlan_table()`, and `mlx4_init_roce_gid_table()`.
- MAC lifecycle: `__mlx4_register_mac()`, `mlx4_register_mac()`, `__mlx4_unregister_mac()`, `mlx4_unregister_mac()`, `__mlx4_replace_mac()`, and `mlx4_get_base_qpn()`.
- VLAN lifecycle: `mlx4_find_cached_vlan()`, `__mlx4_register_vlan()`, `mlx4_register_vlan()`, `__mlx4_unregister_vlan()`, and `mlx4_unregister_vlan()`.
- Bonding helpers: `mlx4_bond_mac_table()`, `mlx4_unbond_mac_table()`, `mlx4_bond_vlan_table()`, and `mlx4_unbond_vlan_table()`.
- RoCE GID partitioning: `mlx4_get_slave_num_gids()`, `mlx4_get_base_gid_ix()`, `mlx4_reset_roce_gids()`, `mlx4_get_slave_from_roce_gid()`, and `mlx4_get_roce_gid_from_slave()`.
- SET_PORT paths: `mlx4_common_set_port()`, `mlx4_SET_PORT_wrapper()`, `mlx4_SET_PORT()`, `mlx4_SET_PORT_general()`, `mlx4_SET_PORT_qpn_calc()`, `mlx4_SET_PORT_user_mtu()`, `mlx4_SET_PORT_user_mac()`, `mlx4_SET_PORT_fcs_check()`, `mlx4_SET_PORT_VXLAN()`, and `mlx4_SET_PORT_BEACON()`.
- Module info: `mlx4_get_module_info()` plus `mlx4_get_module_id()`, SFP/QSFP offset helpers, `struct mlx4_cable_info`, and cable MAD error decoding.

## Control flow and integration
MAC and VLAN registration search the local per-port tables for an existing entry, increment references on reuse, otherwise choose a free slot, mark it valid, and push the whole table to firmware with `MLX4_CMD_SET_PORT`. In multi-function mode public register/unregister APIs call wrapped resource commands instead. In multi-function Ethernet bonding, registration and unregistration may mirror entries to the opposite port at the same index so virtual functions can fail over consistently.

The SET_PORT wrapper converts a slave-visible port to the physical port and sends requests through `mlx4_common_set_port()`. For Ethernet, non-master slaves are restricted to general MTU/user-MTU and GID-table changes. RQP calculation commands are rewritten with the master's base QPN. General commands aggregate maximum MTU/user-MTU across functions and preserve global pause settings unless the master requested the change. GID-table updates validate no duplicate GIDs within the request or against the rest of the port table, merge the slave's partition into the full table, then issue SET_PORT. For InfiniBand, capability masks are aggregated across slaves, with SM and device-management capabilities blocked for guests where required.

Transceiver reads use `MLX4_CMD_MAD_IFC` attribute `0xFF60`. The code first reads the module ID, derives SFP or QSFP I2C address/page/offset semantics, caps each request to `MODULE_INFO_MAX_READ`, avoids crossing the 256-byte page boundary, and returns either the read byte count or a negative command/MAD status.

## State and persistence behavior
Per-port software state lives in `mlx4_priv(dev)->port[port]`: MAC/VLAN entries, reference counters, duplicate flags, RoCE GID tables, base QPN, and mutexes. Multi-function master state records per-slave MTU, user MTU, pause, and InfiniBand capability masks, plus per-port maxima. Hardware-visible state is persistent until reprogrammed: MAC and VLAN tables, RoCE GID tables, port MTU/pause/user MAC/FCS/VXLAN/beacon settings, multicast filters, and IB port capabilities.

## Dependencies
The file depends on mlx4 command mailboxes, `MLX4_CMD_SET_PORT`, `MLX4_CMD_MAD_IFC`, resource reservation commands, mlx4 multi-function helpers, Ethernet and VLAN constants, RoCE GID constants, `mlx4_stats.h`, endian helpers, bitmap helpers for active-port/slave calculations, and device capability fields.

## Risks
- MAC/VLAN bonding requires identical indices on both ports. Partial firmware failure while adding or removing mirrored entries can leave software and hardware tables inconsistent.
- Some duplicate cleanup paths adjust totals on one table while touching another; table counters should be checked carefully after bonding transitions.
- SET_PORT policy is security-sensitive in SR-IOV: guest requests must not change global pause, beacon, SM capability, device management, or unrelated GID slots.
- GID partition math divides VF GID space by active-port membership; zero or stale VF counts can cause bad indexing.
- Module EEPROM reads have page-boundary and high-page quirks; callers must handle short reads and a silent zero-byte return for unsupported SFP high pages.

## Test signals
Test MAC/VLAN register, duplicate register, unregister, replace, exhaustion, and mirrored bond/unbond flows on one-port and two-port devices. Exercise slave SET_PORT denial/allow cases, MTU aggregation across VFs, pause preservation, RoCE GID duplicate rejection and reset, IB capability aggregation, VXLAN and FCS SET_PORT commands, module EEPROM reads for SFP/QSFP/QSFP+/QSFP28, unsupported module IDs, and command failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/profile.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/qp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/qp.c

## Purpose
`qp.c` manages mlx4 queue pair numbering, ICM allocation, lookup, state transitions, special QPs, QP update commands, and RoCE entropy calculation. It is shared by Ethernet, InfiniBand, RoCE, and SR-IOV code that needs to reserve QPNs, map QP context memory, drive firmware QP state machines, and dispatch asynchronous QP events.

## Important APIs, types, and functions
- Lifetime and events: `mlx4_qp_alloc()`, `mlx4_qp_remove()`, `mlx4_qp_free()`, `mlx4_qp_lookup()`, `mlx4_qp_event()`, and `mlx4_put_qp()`.
- State transitions: private `__mlx4_qp_modify()` and exported `mlx4_qp_modify()` plus convenience `mlx4_qp_to_ready()`.
- QPN reservation: `__mlx4_qp_reserve_range()`, `mlx4_qp_reserve_range()`, `__mlx4_qp_release_range()`, and `mlx4_qp_release_range()`.
- ICM mapping: `__mlx4_qp_alloc_icm()`, `mlx4_qp_alloc_icm()`, `__mlx4_qp_free_icm()`, and `mlx4_qp_free_icm()`.
- Table setup: `mlx4_create_zones()`, `mlx4_init_qp_table()`, `mlx4_cleanup_qp_table()`, `mlx4_CONF_SPECIAL_QP()`, and `mlx4_cleanup_qp_zones()`.
- Runtime mutation and query: `mlx4_update_qp()`, `mlx4_qp_query()`, and `mlx4_qp_roce_entropy()`.

## Control flow and integration
QP allocation starts with a QPN reserved from a zone or master resource command, maps all required ICM tables for that QPN, inserts the `struct mlx4_qp` into `dev->qp_table_tree`, and initializes reference/completion state. Async events look up the QP under `qp_table->lock`, take a reference, and call the QP's event callback, which is responsible for dropping the reference.

`__mlx4_qp_modify()` maps current/new state pairs to firmware commands. Reset-to-init also fills MTT base address and page size fields. RTR-to-RTS may compute RoCE v1/v2 entropy by querying the destination QPN. The command mailbox carries the optpar and context, and master devices also update internal QP0 active/proxy state when real or proxy QP0 moves to RTR, ERR, or RST.

QP reservation uses a zone allocator with separate general, RSS, and RAW_ETH/A0 steering areas. BlueFlame-capable Ethernet QPs avoid QPN bits 6 and 7 through `MLX4_BF_QP_SKIP_MASK`. Multi-function callers use wrapped `RES_QP` commands for reserve and ICM mapping. Initialization reserves special QPs, lays out proxy/tunnel SQPs for SR-IOV, creates zones, and configures the firmware special-QP base.

## State and persistence behavior
Runtime state includes `mlx4_priv(dev)->qp_table` locks, zone allocator, bitmaps, ICM tables, RDMARC base/shift from the profile, `dev->qp_table_tree`, special QP bases, and per-port proxy/tunnel QP values. Each `struct mlx4_qp` carries `qpn`, refcount, completion, and callback. Hardware-visible state is QP context, auxiliary/alternate/RDMARC/CMPT mappings, and firmware QP state. QPN reservations persist until explicitly released.

## Dependencies
The file depends on mlx4 command mailboxes, ICM table APIs, zone allocator and bitmap helpers, radix tree APIs, refcount/completion primitives, mlx4 capability fields, RoCE helpers such as `folded_qp()`, and SR-IOV physical capability state.

## Risks
- QP events and free rely on balanced refcounts; callbacks must call `mlx4_put_qp()` or `mlx4_qp_free()` can wait forever.
- State-transition command selection is table-driven; unsupported transitions correctly fail, but caller state tracking must stay synchronized with firmware.
- Zone layout for RSS/RAW_ETH/BlueFlame QPs is bit-mask sensitive. Off-by-one errors can allocate QPNs with forbidden bits or overlap reserved regions.
- Multi-function allocation masks unsupported flags before calling firmware; callers may believe a stronger allocation constraint was honored than hardware actually supports.
- Special QP and proxy/tunnel offsets affect port bring-up and SR-IOV management traffic.

## Test signals
Test QPN reserve/release with alignment, A0 steering, RSS, RAW_ETH, and BlueFlame flags; allocation/free with radix lookup and event dispatch; all valid QP state transitions plus invalid transition rejection; QP0/proxy QP0 state changes on master; `mlx4_update_qp()` capability gating for source-check, VLAN strip, rate limit, and QoS vport; and teardown leak checks for zones and ICM mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/reset.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/reset.c

## Purpose
`reset.c` implements the low-level mlx4 chip reset sequence. It saves selected PCI configuration space, maps the HCA reset register window, obtains the hardware semaphore that excludes flash updates, triggers reset, waits for the device to reappear, and restores PCI/PCIe control registers.

## Important APIs, types, and functions
- The file exports one function: `mlx4_reset(struct mlx4_dev *dev)`.
- Reset-window constants define the BAR0 reset aperture, semaphore offset, reset offset, reset value, and jiffies timeouts.
- It uses PCI config-space helpers, PCIe capability helpers, `ioremap()`/`iounmap()`, `readl()`/`writel()`, `msleep()`, and mlx4 logging.

## Control flow and integration
`mlx4_reset()` allocates a 256-byte buffer for the first 64 PCI config dwords, skips offsets 22 and 23 because they have special device meaning, and records the PCIe capability offset if present. It maps BAR0 plus `0xf0000`, polls the reset-window semaphore for up to 10 seconds, writes the reset value to the reset register, unmaps, waits one second, then polls `PCI_VENDOR_ID` for up to two more seconds until the device no longer reads as `0xffff`.

After the device returns, the function restores PCIe Device Control and Link Control through PCIe capability accessors, restores the first 16 PCI config dwords except `PCI_COMMAND`, and finally restores `PCI_COMMAND`. Any read, map, semaphore, reset, or restore failure aborts with an errno and logs a specific message.

## State and persistence behavior
The function temporarily persists PCI header contents in heap memory. The hardware reset clears device runtime state outside this file, while the restore path writes PCI/PCIe configuration registers back to their saved values. The hardware semaphore is read until it becomes available but is not explicitly released in software; the reset flow relies on device reset semantics.

## Dependencies
Dependencies include the PCI device in `dev->persist->pdev`, BAR0 reset register layout, kernel PCI config accessors, PCIe capability accessors, MMIO mapping, jiffies timeouts, sleeps, endian swab for the reset value, and mlx4 error logging.

## Risks
- Only the first 256 bytes of config space are saved, and only the first 16 dwords are restored after reset aside from PCIe control fields. Devices needing more extended config restoration would require additional handling.
- Failure to obtain the hardware semaphore aborts reset to avoid racing flash updates; callers must propagate or retry `-EAGAIN`.
- If the device takes longer than two seconds to reappear, reset fails with `-ENODEV` even if hardware later recovers.
- Restore order intentionally delays `PCI_COMMAND`; changing it can re-enable memory/bus mastering before other state is ready.

## Test signals
Validation should include successful reset during probe/recovery, simulated config-read/write failures, reset-window mapping failure, semaphore timeout, delayed vendor-ID recovery, PCIe and non-PCIe devices, and post-reset checks that BAR access, interrupts, and DMA setup still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/reset.c -->
