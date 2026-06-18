<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c

Purpose: queued GF1 DRAM DMA engine for PCM and synthesizer transfers. It abstracts ISA DMA programming and GF1 DRAM DMA register setup, with PCM transfers prioritized over synth transfers.

Important APIs/types/functions: `snd_gf1_dma_init()`, `snd_gf1_dma_done()`, `snd_gf1_dma_suspend()`, and `snd_gf1_dma_transfer_block()` are the public entry points. Internals include `snd_gf1_dma_ack()`, `snd_gf1_dma_program()`, `snd_gf1_dma_next_block()`, and `snd_gf1_dma_interrupt()`. It operates on `struct snd_gf1_dma_block` queues stored in `gus->gf1`.

Control flow: clients enqueue a copied DMA block under `dma_lock`. If no transfer is active, the first block is popped and programmed immediately. Hardware interrupt acks the DMA register, invokes the previous block callback, pops the next PCM or synth block, programs it, and frees the queue node. Init installs the DMA-write interrupt handler and uses a shared refcount; done tears down only when the last user leaves.

State and persistence: queue heads/tails, current ack callback/private data, shared count, and trigger flag live in `gus->gf1`; all are volatile. Suspend drains active and queued transfers, calling callbacks so waiters can finish.

Dependencies and integration: uses ISA DMA (`snd_dma_program`, `snd_dma_disable`), GF1 register helpers, `dma_lock`, `dma_mutex`, and default interrupt handlers from reset code. PCM playback uses this for DRAM block uploads.

Risks: address translation differs for 8/16-bit DMA and enhanced mode; unaligned addresses are rejected only by debug return. Callback ordering matters for close waiters. Test signals include PCM block upload progress, queued multiple blocks, synth/PCM priority, suspend while DMA active, high-DMA channels, and no leaked queue nodes after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c -->
