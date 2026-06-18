# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.h

Purpose: shared internal header for Qualcomm HIDMA channel, low-level, and debug code. It defines the TRE layout, low-level ring device state, DMAEngine channel/device state, and cross-file function prototypes.

Important APIs/types/functions: `enum tre_type` selects HIDMA memcpy and memset transaction types. `struct hidma_tre` represents a low-level request slot with allocation state, callback, local TRE words, ring index, interrupt flags, and error fields. `struct hidma_lldev` owns hardware-facing state: TRCA/EVCA mappings, TRE/EVRE coherent rings, pending TRE table, processed offsets, write offset, tasklet, FIFO, and channel states. `struct hidma_desc` wraps `dma_async_tx_descriptor` with a low-level TRE channel number. `struct hidma_chan` owns DMAEngine lists and per-channel status. `struct hidma_dev` owns platform resources, the `dma_device`, IRQ/MSI metadata, debugfs/sysfs state, and issue tasklet.

Control flow: the header expresses the layering boundary. `hidma.c` allocates `hidma_desc` objects and calls `hidma_ll_request`, `hidma_ll_set_transfer_params`, `hidma_ll_queue_request`, and `hidma_ll_start`. `hidma_ll.c` updates status and invokes callbacks. `hidma_dbg.c` reads both `hidma_chan` lists and `hidma_lldev` internals.

State/persistence: all fields are volatile runtime driver state; no persistent storage is involved. Synchronization is expected through `hidma_chan.lock`, `hidma_lldev.lock`, atomics in `hidma_tre`, and runtime PM in the caller.

Dependencies/integration: includes `kfifo`, `interrupt`, and `dmaengine`; assumes Linux DMAEngine cookie/callback semantics and platform MMIO.

Risks: because this header exposes internals across four implementation files, structure changes affect DMAEngine logic, low-level IRQ handling, and debugfs output together. `tre_local` is sized as `HIDMA_TRE_SIZE / sizeof(u32) + 1`, while transfer programming uses fixed index constants; layout changes must preserve hardware format.

Test signals: compile all HIDMA objects together, run memcpy/memset transfer tests, inspect debugfs output for coherent field values, and exercise error completion to confirm `err_info`/`err_code` propagation.
