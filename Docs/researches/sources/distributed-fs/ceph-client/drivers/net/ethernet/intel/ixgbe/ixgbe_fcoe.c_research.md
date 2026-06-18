# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.c

## Purpose

`ixgbe_fcoe.c` implements Fibre Channel over Ethernet offload support for ixgbe when `CONFIG_FCOE` enables the driver's FCoE integration. It covers Direct Data Placement (DDP) context setup/completion, FCoE sequence offload for transmit, FCoE/FIP hardware filter and queue programming, per-CPU DDP DMA pools, enable/disable transitions exposed through netdevice FCoE operations, WWN construction, HBA information reporting, and FCoE traffic-class lookup.

The file bridges Linux libfc/libfcoe to ixgbe hardware offloads. Its most sensitive responsibilities are DMA lifetime management for SCSI scatterlists and hardware DDP/filter context programming by XID.

## Important APIs, types, and functions

Main APIs are `ixgbe_fcoe_ddp_get()`, `ixgbe_fcoe_ddp_target()`, `ixgbe_fcoe_ddp_put()`, `ixgbe_fcoe_ddp()`, `ixgbe_fso()`, `ixgbe_configure_fcoe()`, `ixgbe_setup_fcoe_ddp_resources()`, `ixgbe_free_fcoe_ddp_resources()`, `ixgbe_fcoe_enable()`, `ixgbe_fcoe_disable()`, `ixgbe_fcoe_get_wwn()`, `ixgbe_fcoe_get_hbainfo()`, and `ixgbe_fcoe_get_tc()`. The code uses `struct ixgbe_fcoe`, `struct ixgbe_fcoe_ddp`, `struct ixgbe_fcoe_ddp_pool`, FC/FCoE headers, SCSI scatterlists, ixgbe rings/descriptors, per-CPU DMA pools, and FCoE registers/macros.

## Control flow

DDP setup enters through initiator or target netdevice callbacks and funnels into `ixgbe_fcoe_ddp_setup()`. Setup validates netdev, scatterlist, XID range, adapter state, and context availability; maps the SG list for DMA_FROM_DEVICE; allocates a per-CPU DMA pool descriptor-list buffer; converts SG DMA ranges to hardware buffer base entries; enforces FCoE buffer alignment rules; and appends a shared extra buffer when the final segment exactly fills a hardware buffer. It then builds FCBUFF/FCDMARW/FCFLTRW values and programs either direct X550 per-XID registers or older indirect registers under `fcoe->lock`. Failures unwind DMA pool allocation, SG mapping, and CPU pinning.

DDP put validates the active XID, captures byte count, invalidates hardware context when `ddp->err` is set, waits if the context still reads valid, unmaps the SG list if still owned, frees the descriptor-list DMA pool object, clears the DDP slot, and returns DDPed length. Receive completion in `ixgbe_fcoe_ddp()` parses the FC header, chooses OX_ID or RX_ID based on exchange context, checks descriptor FC error/status bits, records DDP length, unmaps SG lists on FCPRSP, bypasses skb delivery for fully DDPed data, and appends a trailer for target last-sequence frames.

Transmit offload in `ixgbe_fso()` validates FCoE GSO type, resets skb network/transport headers, maps SOF/EOF values to context descriptor flags, handles relative-offset increment, adjusts header length and byte counts for FCoE LSO, marks TX flags for FCoE/CRC, and writes the TX context descriptor.

`ixgbe_configure_fcoe()` enables FCoE EtherType filtering for CRC/DDP classification, and when full FCoE is enabled programs FCRETA queue redirection, enables FCRECTL, installs a FIP filter to the first FCoE queue, and configures FCRXCTRL for CRC byte order and FCoE version. Enable/disable stop the interface if needed, toggle DDP resources and FCoE flags, notify feature changes, rebuild interrupt/queue schemes, and reopen the interface.

## State and persistence behavior

Per-XID DDP state lives in `adapter->fcoe.ddp[]`, with length, error, DMA pool pointer, descriptor-list virtual/DMA address, SG pointer, and SG count. Per-CPU DDP pools store `noddp` and `noddp_ext_buff` counters aggregated into ixgbe stats. Adapter feature state uses FCoE capable/enabled flags, `adapter->fcoe.refcnt`, `adapter->fcoe.mode`, `adapter->fcoe.up`, ring-feature metadata, and `netdev->fcoe_mtu`. Hardware state includes FCoE/FIP filters, redirection table entries, DDP contexts, and FCRXCTRL bits.

## Dependencies and integration points

The file integrates with `ixgbe_main.c` through FCoE netdevice ops, RX cleanup, TX offload, open/close resource setup/teardown, stats aggregation, and hardware configuration. `ixgbe_lib.c` contributes FCoE queue allocation and ring-feature mapping. DCB code controls FCoE priority/traffic class. SR-IOV paths adjust MTU and queue/pool behavior when FCoE is enabled. Linux libfc/libfcoe calls the netdevice hooks and consumes WWN/HBA metadata.

## Risks and edge cases

`ixgbe_fcoe_enable()` increments `fcoe->refcnt` before validation and ignores the return from `ixgbe_fcoe_ddp_enable()`, which can skew reference state or enable FCoE after DDP allocation failure. DDP setup uses `get_cpu()` with multiple unwind paths, so future edits must preserve exactly one `put_cpu()`. DMA map and pool failures must unwind in correct order. Many aligned-storage constraints legitimately fall back to no DDP. X550 and older hardware use different context programming and locking. `ixgbe_fcoe_ddp()` calls `skb_linearize()` without checking failure before `skb_put()`. Enable/disable rebuild queues and are traffic-disruptive. HBA model reporting defaults unknown non-82599/non-X550 devices to X540.

## Test signals

Useful signals include successful FCoE enable/disable, `netdev->fcoe_mtu` toggling, FCoE/FIP filters programmed during open, FCoE queue assignment, DDP setup returning `1` for aligned SG layouts and `0` for unsupported layouts, DDP byte counts on completion, SG unmap on FCPRSP/done, `fcoe_noddp` counter increments on fallback, FSO descriptors for `SKB_GSO_FCOE`, valid WWNN/WWPN from SAN MAC/prefixes, out-of-range XID rejection, adapter down/resetting rejection, missing pool handling, DMA map failure, exact-full final buffer workaround, target last-sequence completion, SR-IOV warning path, and unbalanced enable/disable reference counts.
