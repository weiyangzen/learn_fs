# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.c

Purpose: core platform driver for the Allwinner sun6i ISP. It manages shared DMA tables, hardware resources, runtime PM, interrupt handling, media/V4L2 device registration, and orchestrates proc/capture/params subcomponents.

Important APIs/functions: `sun6i_isp_load_read/write()` access the DMA load table. `sun6i_isp_state_update()` coordinates capture and params pending state and optionally sets `SUN6I_ISP_FE_CTRL_PARA_READY`; `sun6i_isp_state_complete()` marks state applied after PARAM_LOAD. Table helpers allocate/free coherent load/save/LUT/DRC/stats tables and `sun6i_isp_tables_configure()` writes their DMA addresses. `sun6i_isp_interrupt()` handles FINISH and PARA_LOAD in chronological order. Resource setup maps registers with regmap, gets `mod`/`ram` clocks, sets exclusive module clock rate, gets shared reset, requests IRQ, and enables PM runtime. Probe sets up resources, tables, V4L2/media, proc, capture, and params; remove unwinds them.

Control flow: probe obtains variant table sizes from OF match data, allocates shared device state, initializes state lock, resources, DMA tables, V4L2/media objects, proc subdev, capture video node, and params meta-output node. Streaming is driven by proc/capture code; interrupts call capture finish and state complete/update. Runtime resume deasserts reset and enables clocks; suspend asserts reset and disables clocks.

State and persistence: shared `sun6i_isp_device` persists for device lifetime. Coherent DMA tables persist from probe to remove. The load table is the staging state copied into hardware registers on PARAM_READY/PARA_LOAD; this is the core persistence mechanism across frames.

Dependencies/integration: uses clk, DMA coherent memory, IRQ, OF platform matching, PM runtime, regmap MMIO, reset, V4L2/media controller. Integrates with `sun6i_isp_proc`, `capture`, `params`, and register definitions.

Risks: `sun6i_isp_tables_setup()` lacks cleanup of previously allocated tables on intermediate allocation failure; probe error path calls cleanup only after the function returns failure, but it will free all tables regardless of whether later `data` pointers were initialized. The interrupt handler processes enabled status only after checking `status & enable`; disabled-but-pending statuses are acknowledged in `complete`. State locking is split between global `state_lock` and component locks; lock ordering must remain consistent.

Test signals: probe/remove with allocation failure injection, IRQ ordering with FINISH+PARA_LOAD set, runtime PM cycles, table DMA address register programming, media device registration failure unwinds, and stream tests confirming params apply on the intended next frame.
