## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-debugfs.c

### Purpose
`ptdma-debugfs.c` exposes PTDMA/AE4DMA runtime information under the dmaengine debugfs device root. It reports device version, queue counts, total interrupts, per-queue operation counts, and enabled interrupt status.

### Important APIs, Types, And Functions
The exported setup function is `ptdma_debugfs_setup()`. Show callbacks are `pt_debugfs_info_show()`, `pt_debugfs_stats_show()`, and `pt_debugfs_queue_show()`, each wrapped by `DEFINE_SHOW_ATTRIBUTE`.

### Control Flow, State, And Persistence
Setup first checks `debugfs_initialized()`, then creates `info` and `stats` files. For AE4DMA version devices it creates one `qN` directory per AE4 command queue and attaches queue stats to each; for PTDMA it creates a single `q` directory. Reads inspect device registers and in-memory counters on demand; no persistent data is stored by debugfs beyond dentries.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include debugfs, seq_file, `ptdma.h`, AE4 queue types, and dmaengine debugfs root initialization. Risks include reading registers after device teardown if debugfs lifetime is not coupled to dmaengine unregister, version-specific offset assumptions, and unsynchronized counter reads. Test signals include debugfs presence after PTDMA and AE4DMA probe, correct queue directory count, total interrupt counter updates, enabled interrupt text for both versions, and no crashes when debugfs is disabled.
