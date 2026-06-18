# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.c

Purpose: low-level load/store helpers for remote queue descriptors and elements.

Important functions: `ia_css_queue_load`, `ia_css_queue_store`, `ia_css_queue_item_load`, and `ia_css_queue_item_store`.

Control flow: SP-location descriptor fields are accessed byte-by-byte through `sp_dmem_load/store_uint8` respecting ignore flags; HOST location transfers whole descriptors/elements via `hmm_load/store`; ISP location returns `-ENOTSUPP`. Item access uses element address plus `position * sizeof(ia_css_circbuf_elem_t)`.

State/persistence: no owned state. It mutates remote queue memory through SP DMEM or HMM operations.

Dependencies/integration: HMM, SP DMEM accessors, circular-buffer types, and queue handle layout from `queue_access.h`.

Risks: SP descriptor `size == 0` returns `-EDOM` as a workaround for transient bad reads to prevent division by zero. Position is `u8`, so queue sizes/indices must fit. No memory barriers or locking are visible around remote descriptor/item updates.

Test signals: descriptor field ignore masks, SP transient zero-size handling, host HMM transfer correctness, item offset calculation, ISP unsupported path, and invalid pointer returns.
