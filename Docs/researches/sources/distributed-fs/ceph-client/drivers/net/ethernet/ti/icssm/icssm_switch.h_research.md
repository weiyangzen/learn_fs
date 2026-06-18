# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switch.h

## Purpose
This header is the memory-map and descriptor ABI for ICSSM EMAC and switch firmware. It defines queue sizes, descriptor bit fields, PRUSS DRAM/shared-RAM offsets, OCMC buffer offsets, and switch FDB offsets. The driver uses these macros to program firmware-visible memory exactly.

## Important APIs, types, and functions
- Basic sizes: `SWITCH_BUFFER_SIZE`, `ICSS_BLOCK_SIZE`, `BD_SIZE`, `NUM_QUEUES`, host and physical queue depths.
- Buffer descriptor masks/shifts describe packet length, port, broadcast, error, timestamp, lookup success, flood, shadow, and HSR bits.
- DRAM offsets include statistics, storm prevention, PHY speed, port status/control, MAC address, RX interrupt status, and STP invalid state.
- Switch DRAM offsets describe queue descriptors, collision descriptors, collision status, interface/port MAC addresses, size/offset/descriptor tables, and RX/TX contexts.
- EMAC offsets describe TTS and host queue context locations.
- Shared-RAM offsets define host queue descriptors, size/offset tables, promiscuous mode bits, and buffer descriptor pool layout.
- OCMC offsets define buffer regions for host and MII queues.
- FDB offsets define shared-RAM locations and sizes for index table, MAC table, per-port STP config, flood flags, and locks.

## Control flow
This header has no executable control flow. It drives control flow indirectly: queue init functions copy `queue_descs` and queue info into the offsets declared here; TX/RX datapath uses descriptor bit masks; switch FDB code maps typed `__iomem` structures onto FDB offsets.

## State and persistence behavior
All defined addresses refer to volatile PRUSS DRAM/shared RAM or OCMC memory. Values are initialized on driver open and consumed/mutated by firmware during packet processing. No on-disk persistence exists.

## Dependencies and integration points
The header is consumed by `icssm_prueth.h`, `icssm_prueth.c`, and `icssm_prueth_switch.c`. It assumes local FDB structure definitions are visible for `sizeof(struct fdb_...)` macros through include ordering. It is tightly coupled with TI PRU firmware.

## Risks and edge cases
- Most constants are firmware ABI. Renaming, resizing, or reordering can cause runtime memory corruption without compile errors.
- Host queue size macros and buffer offsets must fit in the allocated OCMC size, which differs for AM33xx due to an 8 KiB reserved region.
- `COL_QUEUE_SIZE` is zero while collision descriptors still exist; firmware expectations should be checked.

## Test signals
Validation should include compile-time or runtime offset assertions against firmware ABI, traffic at maximum supported frame size, queue wrap and overflow, descriptor flag parsing, EMAC promiscuous bit updates, and switch FDB shared-memory mapping.
