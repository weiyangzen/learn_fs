# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp.c

## Purpose

`mtk_scp.c` is the MediaTek System Control Processor remoteproc driver. It supports multiple MediaTek SoCs, single-core and dual-core SCP clusters, firmware loading into SRAM/TCM/optional DRAM, IPI buffer setup, rpmsg subdevice creation, watchdog reporting, video capability publication, default firmware-name generation, and system sleep clock handling.

## Important APIs, types, and functions

- Public exports include `scp_get()`, `scp_put()`, `scp_get_device()`, `scp_get_rproc()`, `scp_get_vdec_hw_capa()`, `scp_get_venc_hw_capa()`, and `scp_mapping_dm_addr()`.
- `scp_ipi_handler()` dispatches shared-buffer messages to registered handlers and wakes ack waiters.
- SoC-specific reset/IRQ/pre-load/stop helpers implement MT8183, MT8186, MT8188, MT8192, and MT8195 differences.
- `scp_sram_power_on/off()` sequence SRAM power registers one bit at a time while honoring reserved masks.
- `scp_elf_load_segments()` is a 32-bit ELF loader that uses `scp_memcpy_aligned()` for SRAM writes.
- `scp_elf_read_ipi_buf_addr()` discovers a `.ipi_buffer` ELF section; `scp_ipi_init()` falls back to a SoC default offset and initializes receive/send objects.
- `scp_start()` deasserts reset and waits up to 2 seconds for the `SCP_IPI_INIT` handler to set `run.signaled`.
- Address translators `mt8183_scp_da_to_va()` and `mt8192_scp_da_to_va()` cover SRAM, optional L1TCM, and optional coherent DRAM.
- `scp_rproc_init()`, `scp_add_single_core()`, and `scp_add_multi_core()` build per-core remoteproc instances and cluster lists.

## Control flow

Probe maps the cluster `cfg` region and optional `l1tcm`, initializes the cluster list and lock, populates child `mediatek,scp-core` devices, and then chooses single-core or multi-core setup. Per core, `scp_rproc_init()` parses or generates firmware path, allocates a remoteproc, maps the `sram` resource, gets clocks, initializes optional reserved/coherent memory, initializes IPI locks and waitqueues, registers `SCP_IPI_INIT`, allocates the shared receive buffer, creates an rpmsg subdevice, and requests the IRQ.

Remoteproc prepare prepares the clock. Load enables the clock, asserts reset, runs the SoC pre-load hook to power SRAM/TCM and configure MPU/cache/offset registers, then copies firmware segments. Parse firmware enables the clock and initializes the IPI buffers from `.ipi_buffer` or default offset. Start enables the clock, clears the init signal, deasserts reset, waits for firmware init IPI, disables the clock, and reports the firmware version. Stop enables the clock, asserts reset, runs SoC-specific SRAM/watchdog shutdown, and disables the clock.

Interrupt handling enables the clock, calls the SoC-specific handler, and disables the clock. IPC interrupts dispatch IPI handlers; watchdog conditions report crashes for every core in the cluster. Dual-core MT8188/MT8195 paths refcount shared L2TCM and program core1 address offset registers before booting core1.

## State and persistence behavior

Per-core state includes SRAM mappings, optional coherent DRAM, IPI descriptors, firmware-reported capabilities, current IPI buffers, rpmsg subdevice, and rproc state. Cluster state includes shared register base, optional L1TCM mapping, core list, lock, and L2TCM refcount. Hardware state persists in SCP reset, SRAM power, watchdog, cache, MPU, IPC, and offset registers. The last firmware version and capabilities remain in `scp->run` after boot and are exported to clients.

## Dependencies and integration points

The driver depends on remoteproc, MediaTek SCP public API, MediaTek rpmsg (`mtk_rpmsg_create_rproc_subdev()`), coherent DMA/reserved memory, OF child population, clocks, IRQs, and the shared `mtk_common.h`/`mtk_scp_ipi.c` layer. DT must provide cluster compatible strings, `cfg`, per-core `sram`, optional `l1tcm`, optional `firmware-name`, optional reserved memory, and optional child core nodes for dual-core systems.

## Risks and edge cases

- `scp_get()` returns platform drvdata but does not take an explicit device reference on the SCP device, while `scp_put()` calls `put_device(scp->dev)`. That pairing relies on an external reference path and should be audited with users.
- `scp_mapping_dm_addr()` requests length 0; the address translators accept zero-length ranges and can return base pointers, which is useful but different from several other remoteproc drivers.
- `scp_elf_read_ipi_buf_addr()` parses ELF section tables without the same truncation checks used by some other loaders.
- `scp_ipi_handler()` treats missing handlers as errors and does not clear the hardware IPC bit itself; SoC IRQ handlers must always clear/ack correctly after dispatch.
- Multi-core setup stores parent `pdev` drvdata as the last created core solely to find the cluster on remove. This is documented but fragile if later code assumes parent drvdata is core0.
- Coherent memory allocation is attempted even when `max_dram_size` can be zero; this path depends on DMA API behavior and later unmap skips only by size.
- Shared L2TCM refcounts must remain balanced across load/stop failures for dual-core SoCs.

## Test signals

Build all MediaTek SCP compatibles. Boot tests should cover MT8183/MT8186/MT8188/MT8192/MT8195, single and dual core, default firmware-name generation, `.ipi_buffer` and default IPI offsets, IPI init timeout, rpmsg namespace service, watchdog crash broadcast, coherent DRAM mapping, L1TCM mapping, L2TCM refcounting on failures, and suspend/resume clock prepare handling. Static validation should compare register tables against SoC data and check all per-compatible callbacks are non-NULL.
