# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_av.c

## Purpose
`mthca_av.c` manages UD address vectors and static-rate conversion for Tavor and mem-free Arbel/Sinai devices.

## Important APIs, types, and functions
`struct mthca_av` is the hardware AV layout. `mthca_rate_to_ib()` and `mthca_get_rate()` translate between mthca static-rate encodings and RDMA `enum ib_rate`, with separate Tavor and mem-free formulas. `mthca_create_ah()`, `mthca_destroy_ah()`, `mthca_read_ah()`, `mthca_ah_query()`, `mthca_ah_grh_present()`, `mthca_init_av_table()`, and `mthca_cleanup_av_table()` implement AH lifecycle and table setup.

## Control flow
AH creation chooses kmalloc AVs for mem-free devices, on-HCA DDR AV slots for Tavor when allowed, or DMA-pool PCI memory as fallback. It fills port, PD, DLID/path bits, SL, static rate, GRH fields, and qkey-related data, then copies on-HCA AVs to mapped DDR space. Query/read paths reconstruct RDMA AH attributes or UD headers for non-on-HCA AVs. Table init creates an ID allocator, DMA pool, and optional DDR mapping.

## State and persistence
AH state persists in `struct mthca_ah`: allocation type, AV pointer or HCA DMA/DDR address, and key. Tavor can persist AV contents in HCA-attached DDR; PCI-pool AVs persist in coherent DMA memory; mem-free AVs are normal kernel memory used during posting.

## Dependencies and integration points
It depends on RDMA AH helpers, port active rate cached by `mthca_mad.c`, PD local DMA lkey, PCI BAR4 DDR mapping, DMA pools, and send WQE construction in QP code.

## Risks
Fallback from on-HCA allocation must free partially allocated indexes and temporary AV memory correctly. `mthca_read_ah()` and `mthca_ah_query()` intentionally reject on-HCA AVs, limiting observability. Rate conversion depends on old firmware quirks and `stat_rate_support`; wrong conversion can silently misprogram packet pacing. GRH gid-index computation assumes table length and port numbering are valid.

## Test signals
Test AH creation/destruction on mem-free, Tavor with visible DDR, Tavor with hidden DDR, exhausted DDR AV table fallback, DMA pool allocation failure, GRH and non-GRH AVs, AH query/read behavior, static-rate conversion for old firmware support masks, and repeated create/destroy under dma-debug.
