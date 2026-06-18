# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.c

Purpose: implements PDS VFIO dirty-page logging using firmware SEQ_ACK bitmaps.

Important APIs and functions: `pds_vfio_dma_logging_start()`, `pds_vfio_dma_logging_stop()`, `pds_vfio_dma_logging_report()`, bitmap allocation/free helpers, dirty region construction, `pds_vfio_dirty_seq_ack()`, and bitmap processing into VFIO `iova_bitmap`.

Control flow: start marks host VF migration in progress, confirms dirty logging is disabled and supported, combines IOVA ranges if firmware has fewer region slots, sends region descriptors to firmware, allocates per-region host sequence/ack bitmaps and DMA SGLs, and marks logging enabled. Report validates that the requested IOVA range is inside a tracked region, computes bitmap offset/length in 64-bit aligned chunks, reads device sequence bits, XORs with host ack bits, sets dirty IOVAs, copies seq to ack, and writes ack back. Stop disables firmware tracking, frees SGLs/bitmaps/regions, and clears host VF migration status.

State and persistence: `struct pds_vfio_dirty` owns an array of regions and enabled flag. Each region stores host bitmaps, device bitmap offset, SGL DMA address, start/size/page size, and region bitmap byte count. All state is in memory and cleaned on stop, close, reset error, or failed enable.

Dependencies and integration: depends on PDS admin commands, interval trees from VFIO ranges, DMA mapping through the PF device, vmalloc-backed bitmap pages, and VFIO log ops.

Risks: range math and bitmap offset alignment are critical; mistakes can miss or over-report dirtied pages. The code assumes requests fit a single tracked region. DMA direction differs for read_seq and write_ack and must be synchronized correctly.

Test signals: start with overlapping/many IOVA ranges, firmware max-region combining, unsupported dirty type, zero-length and out-of-region report rejection, 64-bit bitmap alignment, dirty XOR/ack correctness, stop idempotency, and failure cleanup after partial allocation.
