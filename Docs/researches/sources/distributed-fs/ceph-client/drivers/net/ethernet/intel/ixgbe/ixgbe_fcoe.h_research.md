# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.h

## Purpose

`ixgbe_fcoe.h` defines the driver-private data model and constants for ixgbe Fibre Channel over Ethernet support. It is included through `ixgbe.h` when `IXGBE_FCOE` is enabled and supplies the shared types consumed by `ixgbe_fcoe.c`, `ixgbe_lib.c`, `ixgbe_main.c`, DCB netlink handlers, ethtool stats, and queue layout code. The header does not implement logic; its importance is that it fixes DDP table sizing, DMA alignment, default traffic class, and the per-adapter FCoE state shape.

## Important APIs, Types, and Constants

The file imports FC/FCoE protocol definitions from `<scsi/fc/fc_fs.h>` and `<scsi/fc/fc_fcoe.h>`. Key constants include `IXGBE_RXDADV_FCSTAT_SHIFT` for extracting FC status from advanced Rx descriptors, `IXGBE_BUFFCNT_MAX`, `IXGBE_FCPTR_ALIGN`, and `IXGBE_FCPTR_MAX` for DDP user descriptor list layout, and `IXGBE_FCBUFF_*` values for encoded buffer sizes from 4 KiB through 64 KiB. `IXGBE_FCOE_DDP_MAX` is the legacy 512-XID limit, while `IXGBE_FCOE_DDP_MAX_X550` expands storage to 2048 XIDs for newer hardware. `IXGBE_FCOE_DEFTC` defaults FCoE to traffic class 3, and `IXGBE_FCERR_BADCRC` records the descriptor error bit for bad FC CRC.

`struct ixgbe_fcoe_ddp` records one direct data placement context: completed length and error, scatter-gather list count/pointer, DMA address of the user descriptor pointer table, virtual user descriptor list, and the DMA pool used for allocation. `struct ixgbe_fcoe_ddp_pool` is per-CPU storage for a DMA pool plus `noddp` and `noddp_ext_buff` counters used later in statistics. `struct ixgbe_fcoe` is embedded in `struct ixgbe_adapter` and owns the percpu DDP pools, a reference count, a spinlock, the fixed DDP array, an optional extra DDP bounce buffer and DMA address, mode bits such as `__IXGBE_FCOE_TARGET`, and the selected user priority.

## Control Flow and Integration Points

The control flow is external. During probe/init, `ixgbe_main.c` initializes `adapter->fcoe.lock`, sets `adapter->fcoe.up` to `IXGBE_FCOE_DEFTC`, configures feature limits, and calls `ixgbe_setup_fcoe_ddp_resources()`. The `net_device_ops` table wires FCoE callbacks to `ixgbe_fcoe_ddp_get()`, `ixgbe_fcoe_ddp_target()`, `ixgbe_fcoe_ddp_put()`, enable/disable hooks, WWN lookup, and HBA info. Receive handling checks FCoE packet type and calls `ixgbe_fcoe_ddp()` to consume the DDP context, while transmit offload paths call `ixgbe_tx_ctxtdesc()` with FCoE SOF/EOF state. `ixgbe_lib.c` consults `RING_F_FCOE` feature data to reserve or share queue indices with RSS, DCB, and SR-IOV.

## State and Persistence Behavior

All state is in memory and tied to the adapter lifetime. DDP entries track outstanding XIDs and DMA mappings; `ixgbe_fcoe_ddp_put()` and resource teardown clear them. The percpu pool counters are runtime statistics aggregated into hardware stats, not persisted across module unload or device reset. The `mode` bitmap records target-mode use for the active adapter instance. The default priority may be overridden by DCB application settings and is restored from driver initialization on fresh probe.

## Dependencies

This header depends on Linux SCSI FC/FCoE headers, scatterlists, DMA pools, atomics, spinlocks, percpu allocation, and ixgbe adapter definitions that include it. Queue consumers also depend on DCB and FCoE compile-time feature gates.

## Risks and Test Signals

The fixed `ddp[2048]` array makes table bounds critical; every XID user must honor `netdev->fcoe_ddp_xid` and hardware-specific limits. DMA address list alignment and buffer-size encodings must match hardware expectations or DDP can corrupt data or silently fall back. Locking around shared DDP entries is required because completion, setup, and teardown can race. Useful tests include FCoE enable/disable cycles, DDP setup/done with boundary XIDs, target-mode setup, reset while DDP is active, DCB priority changes, queue count changes with FCoE enabled, and ethtool stat checks for `fcoe_noddp` and CRC/drop counters.
