# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.c

Implements cx18 DMA buffer and MDL queue management for streams moving between driver ownership and CX23418 firmware ownership. It maintains `q_idle`, `q_free`, `q_busy`, and `q_full`, with atomic depths and spinlocked lists. Important APIs include `cx18_queue_init`, `_cx18_enqueue`, `cx18_dequeue`, `cx18_queue_get_mdl`, `cx18_load_queues`, `cx18_unload_queues`, `cx18_stream_alloc`, and `cx18_stream_free`.

Control flow starts with allocation of MDLs and DMA-mapped buffers, then `cx18_load_queues` writes buffer physical addresses and lengths into `cx->scb->cpu_mdl` and moves usable MDLs to `q_free`. Firmware completions are reconciled from `q_busy` by ID; skipped MDLs are detected, warned about, and returned to rotation. State is volatile memory, DMA mappings, queue metadata, and firmware-visible SCB entries.

Dependencies include PCI DMA APIs, cx18 SCB IO helpers, stream metadata, Linux lists, atomics, and spinlocks. Risks are DMA coherency mistakes, SCB reserved area exhaustion, firmware/driver MDL desynchronization, and calling unload while stream activity still touches unlocked `buf_pool`. Test signals include capture start/stop stress, skipped-MDL warnings, DMA allocation failures, and VBI/YUV multi-buffer MDL sizing.
