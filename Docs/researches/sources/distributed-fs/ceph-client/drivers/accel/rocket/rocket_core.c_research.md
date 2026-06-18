# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.c

Purpose: initializes and tears down one physical Rockchip NPU core.

Important APIs and types: exports `rocket_core_init`, `rocket_core_fini`, and `rocket_core_reset`, operating on `struct rocket_core` from `rocket_core.h`.

Control flow: init obtains two resets (`srst_a`, `srst_h`), four clocks, maps `pc`, `cna`, and `core` register resources, sets DMA segment size and 40-bit coherent mask, gets the IOMMU group, initializes job scheduling/IRQ state, enables runtime PM with a 50 ms autosuspend delay, briefly resumes the device to read/version-log hardware, then autosuspends. Fini disables runtime PM, drops the IOMMU group, and finalizes job scheduling. Reset asserts/deasserts resets with a 10 us delay.

State and persistence: core state includes MMIO pointers, clocks, reset controls, IOMMU group, runtime PM state, and scheduler state initialized through `rocket_job_init`.

Dependencies and integration: used by platform probe/remove in `rocket_drv.c`; depends on reset, clock, IOMMU, PM runtime, and register macros.

Risks and test signals: validate resource names in device tree, PM balance on init failure, IOMMU group lifetime, version register access after resume, and reset behavior during scheduler timeout.
