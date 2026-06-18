# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/ah.c

## Purpose
`ah.c` implements MANA RDMA address-handle creation and destruction for RoCE-style UD/GSI sends.

## Important APIs, Types, And Functions
`mana_ib_create_ah()` validates that the requested AH is RoCE and has a GRH, rejects user-data creation, allocates a `struct mana_ib_av` from the device DMA pool, and fills destination/source IP, destination MAC, UDP source port, hop limit, DSCP, and IPv4/IPv6 format bits. `mana_ib_destroy_ah()` frees the AV buffer back to the pool. `copy_in_reverse()` from `mana_ib.h` is used because MANA firmware expects reversed byte order for addresses.

## Control Flow
Create validates the AH type and GRH flag, allocates DMA-coherent AV storage, reads the GRH, derives the network type from `sgid_attr`, copies the destination MAC, derives UDP source port from flow label, and fills IPv6 or IPv4-mapped address fields. Destroy unconditionally returns the pool allocation.

## State And Persistence
Each `struct mana_ib_ah` owns one DMA-pool allocation and DMA address for the AV. State is tied to the RDMA AH lifetime and is not persisted. The AV contents are consumed later by send posting, where the AV DMA address is passed as the first SGE.

## Dependencies And Integration Points
The file integrates with RDMA core AH callbacks, GRH/GID helpers, the MANA AV DMA pool created in `device.c`, and `wr.c` send posting. It expects `grh->sgid_attr` to be valid for network-type and source-GID access.

## Risks
Only kernel-created AHs are supported; unexpected `udata` returns `-EINVAL`. Missing or invalid `sgid_attr` would be unsafe because create dereferences it after validation of GRH only. Endianness is hardware-specific, so address reversal must match firmware ABI. Destroy assumes `ah->av` is initialized.

## Test Signals
Test IPv4 and IPv6 RoCE AH creation, GRH-missing rejection, non-RoCE rejection, udata rejection, DMA-pool allocation failure, address/DSCP/port encoding, and send path use followed by AH destroy.
