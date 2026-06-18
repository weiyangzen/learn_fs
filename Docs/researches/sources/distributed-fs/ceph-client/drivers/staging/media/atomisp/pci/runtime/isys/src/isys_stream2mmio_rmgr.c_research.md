# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.c

Purpose: allocates stream2mmio stream IDs per stream2mmio block.

Important functions/state: static `isys_stream2mmio_rsrc[N_STREAM2MMIO_ID]`; init/uninit clear all entries; acquire uses `N_STREAM2MMIO_SID_PROCS[stream2mmio]` and a bitmap to return the first free SID; release clears an active SID.

Control flow: acquire validates block and output pointer, checks active count, scans from `STREAM2MMIO_SID0_ID` to max SID, sets the bit and counter. Release validates range and active bit before clearing.

State/persistence: global per-block bitmap/counter state persists until uninit; no locking.

Dependencies/integration: `virtual_isys.c` allocates one SID per data/metadata channel and releases it on stream destroy.

Risks: caller must pair acquire/release exactly. No owner tracking or synchronization. Bitmap width assumes SID count fits in 32 bits.

Test signals: per-block exhaustion, release/reacquire reuse, invalid SID release no-op, init/uninit clearing every stream2mmio ID, and multi-stream setup serialization.
