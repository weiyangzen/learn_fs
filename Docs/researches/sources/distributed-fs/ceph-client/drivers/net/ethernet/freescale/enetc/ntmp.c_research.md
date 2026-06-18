# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp.c

## Purpose
Provides the NETC Table Management Protocol 2.0 library used by ENETC4 to manage hardware tables through a NETC control BD ring, currently MAC Address Filter Table and RSS Table operations.

## Important APIs, Types, and Functions
Exports `ntmp_init_cbdr`, `ntmp_free_cbdr`, `ntmp_maft_add_entry`, `ntmp_maft_query_entry`, `ntmp_maft_delete_entry`, `ntmp_rsst_update_entry`, and `ntmp_rsst_query_entry`. Internal helpers include `netc_xmit_ntmp_cmd`, `ntmp_clean_cbdr`, `ntmp_alloc_data_mem`, `ntmp_fill_request_hdr`, `ntmp_fill_crd_eid`, `ntmp_delete_entry_by_id`, and `ntmp_query_entry_by_id`.

## Control Flow
CBDR init allocates coherent descriptors with extra space for 128-byte alignment, allocates software CBD tracking entries, records register pointers, initializes indices from hardware, writes base/length, and enables the ring. Command transmit cleans the ring when enough BDs are used, copies request CBD and software buffer metadata into the next slot, updates PIR, polls CIR for completion, checks system bus and NTMP response errors, copies writeback CBD, and leaves buffer cleanup to later ring cleaning/free. Table helpers allocate 32-byte-aligned coherent data buffers, fill NTMP v2 headers and request data, serialize access through the selected ring mutex, transmit, decode query data, and log table-specific failures.

## State and Persistence
State includes CBDR hardware registers, aligned descriptor memory, coherent per-command data buffers, software CBD metadata, producer/consumer indices, ring mutex, table versions in `ntmp_user->tbl`, MAFT entries, and the 64-entry RSS table.

## Dependencies and Integration Points
Used by `enetc4_pf.c` for MAFT exact unicast filters and by `enetc_cbdr.c`/ethtool for ENETC4 RSS get/set. Depends on `ntmp_private.h`, `linux/fsl/netc_global.h` register access, DMA APIs, vmalloc, and iopoll.

## Risks
Risks include delayed cleanup of successful command buffers until later CBDR cleaning, fixed one-ring selection, strict RSS count of 64 entries, response layout assumptions, alignment math for DMA and virtual buffers, and table-version assumptions initialized to zero for ENETC 4.1.

## Test Signals
Initialize/free CBDR repeatedly, set/query/delete MAFT entries from receive-mode changes, set/query RSS table through ethtool, force command timeout/SBE/response error paths, test ring wrap and cleanup under many commands, and inspect ENETC4 debugfs MAFT output against expected filters.
