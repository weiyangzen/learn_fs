
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/hisi_ptt.c

Purpose: HiSilicon PCIe Tune and Trace driver. It exposes tuning controls through sysfs, registers a perf AUX PMU for tracing PCIe TLP headers, manages DMA trace buffers and interrupts, and dynamically publishes filters for root ports/requesters under the managed PCIe core.

Important APIs/types/functions: tune attributes use `hisi_ptt_tune_attr_show/store()`. Trace lifecycle uses `hisi_ptt_trace_start()`, `hisi_ptt_trace_end()`, `hisi_ptt_update_aux()`, and `hisi_ptt_isr()`. Filter lifecycle uses `hisi_ptt_alloc_add_filter()`, sysfs create/remove helpers, PCI bus notifier `hisi_ptt_notifier_call()`, delayed work `hisi_ptt_update_filters()`, and initial bus walk `hisi_ptt_init_filters()`. Perf hooks include `event_init`, `setup_aux`, `free_aux`, `start`, `stop`, `add`, `del`, and CPU hotplug migration.

Control flow: probe rejects non-identity IOMMU mappings, enables PCI BAR 2, sets 64-bit coherent DMA, registers MSI, allocates four coherent 4 MiB hardware trace buffers, reads supported BDF range, walks the PCI bus to seed filters, registers a PCI hotplug notifier, registers a node-local perf PMU named from SICL/core IDs, and creates sysfs filter attributes. Perf start validates config fields, begins AUX output, configures filter/direction/type/format, resets DMA, zeroes buffers, unmasks interrupts, and enables trace. Interrupts copy a full hardware buffer into perf AUX and rotate to the next buffer. Stop disables trace, waits idle, copies residual bytes from write-status, and updates perf state.

State and persistence: volatile `struct hisi_ptt` stores trace control, current CPU, DMA buffer descriptors, filter lists, port mask, notifier/work items, locks, FIFO, and PMU object. Sysfs attributes reflect current in-memory filter/tune state. Trace data persists only in perf AUX buffers supplied by userspace.

Dependencies and integration: depends on PCI, DMA coherent allocation, perf AUX infrastructure, cpuhotplug, MSI interrupts, IOMMU identity mapping, sysfs attribute groups, PCI bus notifier, kfifo, workqueues, and bitfield helpers.

Risks: direct DMA requirement means systems with translated IOMMU domains cannot trace. `hisi_ptt_pmu_add()` returns 0 for CPUs outside the device node without starting, which users must interpret carefully. Interrupt/AUX buffer updates assume enough AUX space and stop trace on failure. Filter list updates can overflow the small FIFO under heavy hotplug. Tune registers are serialized by `tune_lock`; perf trace by `pmu_lock`; filter/sysfs by `filter_lock`, so lock ordering should remain simple. IRQ affinity and CPU hotplug migration are correctness-sensitive.

Test signals: probe on supported Huawei device, reject non-identity IOMMU, inspect PMU format/cpumask/filter/tune groups, run `perf record -e hisi_ptt*/.../` with legal and illegal filters, force AUX buffer exhaustion, handle PCI hotplug add/remove, CPU offline during active trace, and tune read/write timeout paths.
