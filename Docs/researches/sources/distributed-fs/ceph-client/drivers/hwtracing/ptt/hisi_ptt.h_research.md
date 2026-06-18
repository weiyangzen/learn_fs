
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.h

Purpose: private declarations, register definitions, perf config masks, constants, and state structures for the HiSilicon PTT driver.

Important APIs/types/functions: defines `DRV_NAME`, all tuning/trace/status/location register offsets and masks, DMA buffer counts/sizes/timeouts, perf config bit masks, filter group names, and the core structures `hisi_ptt_tune_desc`, `hisi_ptt_dma_buffer`, `hisi_ptt_trace_ctrl`, `hisi_ptt_filter_desc`, `hisi_ptt_filter_update_info`, `hisi_ptt_pmu_buf`, and `struct hisi_ptt`.

Control flow: no standalone execution. `hisi_ptt.c` uses these definitions to program hardware, validate perf configs, publish sysfs filters, allocate AUX mappings, and manage hotplug updates.

State and persistence: describes runtime state stored in `struct hisi_ptt`, including filter lists, delayed work, PMU, locks, DMA buffers, BDF range, and trace session fields. No on-disk persistence.

Dependencies and integration: includes PCI, perf, kfifo, mutex/spinlock, notifier, workqueue, cpumask, and device headers. `to_hisi_ptt()` converts a `struct pmu` back to device state.

Risks: register masks and bitfield widths define ABI-visible perf config parsing. The `direction`, `filter`, `format`, and `type` bitfields in `hisi_ptt_trace_ctrl` must hold validated values exactly. DMA buffer size/count constants drive both hardware programming and AUX-space requirements.

Test signals: compile-time checks through `hisi_ptt.c`, perf format sysfs content, trace start with boundary config values, and hardware register programming inspection.
