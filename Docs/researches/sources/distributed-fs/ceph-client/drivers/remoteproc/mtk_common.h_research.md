# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_common.h

## Purpose

`mtk_common.h` is the private shared header for the MediaTek SCP remoteproc driver and its IPI helper. It defines SoC register offsets and bit masks for MT8183, MT8186, MT8188, MT8192, and MT8195 SCP cores, plus the data structures that connect the core remoteproc driver, rpmsg/IPI layer, multi-core cluster state, and SoC-specific operation tables.

## Important APIs, types, and data

- Register macros cover reset, host/SCP IPC, watchdog, SRAM power-down, cache control, L2TCM/L1TCM power, dual-core IPC, system status, SRAM offset, and secure control registers.
- `SCP_FW_VER_LEN` fixes firmware version string storage at 32 bytes.
- `struct scp_run` carries firmware-ready signal, firmware version, video decode/encode capabilities, and the waitqueue used by boot.
- `struct scp_ipi_desc` protects each IPI handler/private pointer with a mutex.
- `struct mtk_scp_sizes_data` defines firmware DRAM reservation size and IPI buffer size.
- `struct mtk_scp_of_data` is the SoC/core operation table: clock get, pre-load setup, IRQ handler, reset assert/deassert, stop, address translation, IPC register/bit, IPI buffer offset, and sizes.
- `struct mtk_scp_of_cluster` stores shared register mappings, optional L1TCM, a list of SCP cores, cluster lock, and shared L2TCM refcount.
- `struct mtk_scp` is the per-core state used by both `mtk_scp.c` and `mtk_scp_ipi.c`.
- `struct mtk_share_obj` describes the shared SRAM IPI object layout.
- Exported helper prototypes are `scp_memcpy_aligned()`, `scp_ipi_lock()`, and `scp_ipi_unlock()`.

## Control flow

The header has no executable flow. Consumers fill `struct mtk_scp_of_data` per compatible, allocate `struct mtk_scp` per core, and use the register macros in start/load/stop/IRQ/IPI paths. The IPI file uses `struct mtk_share_obj`, `struct scp_ipi_desc`, and locks from this header to register and send messages.

## State and persistence behavior

The structures model persistent SCP hardware state but do not manage it directly. `struct mtk_scp_of_cluster` coordinates shared L2TCM power state through `l2tcm_refcnt`; `struct mtk_scp` stores live mailbox/IPI buffers, DMA memory, and rpmsg subdevice pointers; `scp_run` persists the last firmware-reported version and capability values until overwritten by the next boot.

## Dependencies and integration points

This header includes Linux interrupt, kernel, platform, remoteproc, and public MediaTek SCP API headers. It is tightly coupled to `mtk_scp.c`, `mtk_scp_ipi.c`, `linux/remoteproc/mtk_scp.h`, and the MediaTek rpmsg bridge.

## Risks and edge cases

- A macro typo `MT8186_SCP_L1_SRAM_PD_p2` uses lowercase `p`, which is harmless to C but inconsistent.
- Register offsets are shared across several SoCs with subtle differences; incorrect reuse in an `mtk_scp_of_data` table can reset or power-gate the wrong core.
- `struct mtk_share_obj` declares `u8 *share_buf`, but the code treats the field as an in-SRAM flexible payload location. This ABI is layout-sensitive and should not be changed casually.
- Cluster-level refcounting assumes all L2TCM users hold the same `cluster_lock` discipline.

## Test signals

Compile all MediaTek SCP compatibles and both single-core and dual-core data tables. Static checks should verify every `mtk_scp_of_data` fills all required callbacks and size pointers. Runtime tests should validate register offsets against datasheets for each SoC, especially dual-core IPC/reset/watchdog and L2TCM offset registers.
