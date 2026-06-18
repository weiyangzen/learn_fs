# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.c

## Purpose
`fimc-is.c` is the main Exynos4x12 FIMC-IS platform driver. It manages clocks, firmware and setfile loading, coherent firmware memory, Cortex-A5 ISP CPU power control, mailbox IRQ handling, sensor discovery, subdevice registration, runtime PM, debugfs firmware logs, and module init/exit including the ISP I2C adapter driver.

## Important APIs, Types, and Functions
Clock helpers are `fimc_is_get_clocks()`, `fimc_is_put_clocks()`, `fimc_is_setup_clocks()`, `fimc_is_enable_clocks()`, and `fimc_is_disable_clocks()`. Firmware/memory helpers include `fimc_is_request_firmware()`, `fimc_is_load_firmware()`, `fimc_is_alloc_cpu_memory()`, `fimc_is_free_cpu_memory()`, `fimc_is_load_setfile()`, and `fimc_is_start_firmware()`. Hardware sequencing uses `fimc_is_cpu_set_power()`, `fimc_is_wait_event()`, `fimc_is_hw_open_sensor()`, and `fimc_is_hw_initialize()`. IRQ handling is split between `fimc_is_irq_handler()` and `fimc_is_general_irq_handler()`. Probe/remove and PM are implemented by `fimc_is_probe()`, `fimc_is_remove()`, runtime/system PM callbacks, and module init/exit.

## Control Flow
Module init first registers the ISP I2C driver, then the FIMC-IS platform driver. Probe allocates `struct fimc_is`, maps MCUCTL and PMU registers, parses IRQ, gets clocks, requests IRQ, enables runtime PM, resumes the device, sets DMA segment limits, populates child platform devices, registers ISP/sensor subdevs, creates debugfs, and starts asynchronous firmware loading. Firmware loading validates size, allocates aligned coherent memory, copies firmware, extracts description/version strings, initializes shared chip fields, stores the firmware pointer, and later `fimc_is_start_firmware()` copies it into working memory and powers the A5. Initialization opens the first sensor, obtains and loads the setfile, checks firmware magic, streams off, uploads initial parameters for all scenarios, and marks init done.

## State and Persistence
`struct fimc_is` holds all runtime state: clocks, MMIO bases, IRQ waitqueue, state bits, sensor index, firmware/setfile metadata, DMA memory, shared parameter and shared-info pointers, ISP/sensor subdevices, face-detection header, per-scenario configs, locks, and debugfs dentry. Firmware and setfile contents reside in coherent memory during operation. There is no filesystem persistence beyond loading firmware files from the kernel firmware search path.

## Dependencies and Integration Points
The driver depends on OF address/IRQ/graph/platform population, firmware loader, DMA coherent allocation, vb2 DMA-contig segment limits, runtime PM, common clock, debugfs, FIMC-IS command/register/parameter/error helpers, FIMC ISP subdevice code, FIMC-IS sensor metadata, media-device pipeline infrastructure, and the ISP I2C adapter driver. It matches `samsung,exynos4212-fimc-is`.

## Risks and Edge Cases
Firmware loading is asynchronous; users must not assume firmware memory is ready before state indicates it. The firmware pointer is intentionally retained and replaced after releasing any previous one, so cleanup must release it exactly once. Memory alignment is checked against a 26-bit mask and rejects unsuitable DMA addresses. Sensor parsing supports a bounded sensor array but increments after parsing; index limit handling must prevent overflow. Many command waits depend on IRQ state bits being set by firmware replies. System suspend returns `-EBUSY` if the A5 is powered. PMU lookup supports a deprecated child-node fallback. Several error paths after runtime resume must unwind clocks, IRQ, PMU mapping, subdevs, debugfs, and DMA memory.

## Test Signals
Validate probe with complete and missing DT resources, clock parent/rate programming, runtime PM enable/disable, firmware request success/failure and size bounds, coherent memory alignment failure injection, A5 power-on/off status, firmware boot handshake, sensor open and setfile load, magic-number validation, initial parameter uploads for all scenarios, general IRQ replies including not-done errors, frame-done ISP IRQ dispatch, debugfs `fw_log`, suspend refusal while A5 is powered, and module init unwind when either I2C or platform registration fails.
