# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_dma.c

## Purpose
This file implements the TI Keystone Navigator packet DMA helper driver. It discovers packet DMA instances from device tree, exposes channel open/close APIs to client drivers, and programs TX channels, RX flows, priorities, queue-manager base addresses, and teardown behavior.

## Important APIs, Types, And Functions
Main structs are `knav_dma_pool_device`, `knav_dma_device`, and `knav_dma_chan`, with register structs for global, channel, TX scheduler, and RX flow blocks. Exported APIs are `knav_dma_device_ready`, `knav_dma_open_channel`, and `knav_dma_close_channel`. Internal helpers include `chan_start`, `chan_stop`, `chan_teardown`, `knav_dma_hw_init`, `knav_dma_hw_destroy`, `of_channel_match_helper`, `pktdma_get_regs`, and `dma_init`.

## Control Flow
`knav_dma_probe` creates a singleton pool device, enables runtime PM, and initializes each child DMA node. `dma_init` maps global/TX/RX/scheduler/flow register windows, reads navigator cloud queue-manager addresses, optional loopback/enable-all settings, timeout, and creates TX channel plus RX flow objects. Clients call `knav_dma_open_channel`, which resolves phandle/name arguments from `ti,navigator-dmas`, finds the DMA instance and channel/flow, checks compatible reuse configuration, initializes DMA hardware on first user, and programs registers. Close decrements channel and device refcounts, stopping the channel and hardware on last user.

## State And Persistence
State is singleton global `kdev`, `device_ready`, per-DMA refcounts, per-channel refcounts and cached config, lists of DMA instances/channels, spinlocks, and debugfs visibility. Hardware state persists in packet DMA registers until stop/destroy or device reset.

## Dependencies And Integration Points
The driver depends on OF properties `ti,navigator-cloud-address`, `ti,navigator-dmas`, `ti,navigator-dma-names`, optional `ti,enable-all`, `ti,loop-back`, and `ti,rx-retry-timeout`. It integrates with Keystone QMSS queue numbering, runtime PM, debugfs, and public `linux/soc/ti/knav_dma.h` clients.

## Risks And Test Signals
Risks include singleton limitations, race potential around global lists without broad locking, refcount underflow on bad close calls, teardown timeout, invalid phandle names, and shared channel config mismatches. Test signals include debugfs `knav_dma`, successful channel open/close cycles, expected register programming for TX/RX directions, teardown timeout absence, and packet traffic through QMSS-backed queues.
