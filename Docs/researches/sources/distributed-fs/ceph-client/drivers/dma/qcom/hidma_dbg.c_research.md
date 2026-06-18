# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_dbg.c

Purpose: adds debugfs inspection for Qualcomm HIDMA devices and channels. It is observational only and dumps descriptor/TRE, ring, and resource state for diagnosis.

Important APIs/types/functions: `hidma_ll_chstats` prints one TRE slot, including allocation, queue state, error fields, callback pointer, source/destination DMA addresses, and length. `hidma_ll_devstats` prints low-level device state, ring addresses, ring sizes, processed offsets, and pending TRE count. `hidma_chan_show` prints channel-level paused/signature state and walks `prepared`, `active`, and `completed` lists. `hidma_dma_show` prints descriptor count and TRCA/EVCA resource addresses. `hidma_debug_init` creates debugfs directories and files; `hidma_debug_uninit` removes them.

Control flow: after `hidma.c` registers the DMAEngine channel, `hidma_debug_init` creates a top-level directory named after the device, a `chanN/stats` file for each DMAEngine channel, and a device-level `stats` file. Reading channel stats resumes the device with runtime PM, prints list and low-level state, then marks last busy and autosuspends.

State/persistence: no persistent state beyond debugfs dentries and generated channel debug names. It reads live driver lists without taking the HIDMA channel lock while iterating, so output is diagnostic and may race with active transfers.

Dependencies/integration: depends on debugfs, seq_file `DEFINE_SHOW_ATTRIBUTE`, runtime PM, and internal structures from `hidma.h`.

Risks: exposes kernel virtual addresses and callback pointers through debugfs, suitable for privileged debugging only. List iteration without locks can report transient state. Runtime PM calls in read path can perturb power state during diagnostics.

Test signals: debugfs directory/files appear after probe, disappear after remove, reads succeed during idle and active transfers, and `pending_tre_count`/offsets change consistently under DMAEngine tests.
