# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bestcomm.c

Purpose: Core driver for the MPC52xx BestComm/SDMA communication coprocessor. It initializes shared SRAM structures, maps SDMA registers, exposes task allocation/loading/control APIs, and registers as an early platform driver.

Important APIs/types/functions: `bcom_eng` is the exported global engine pointer. Exported APIs include `bcom_task_alloc`, `bcom_task_free`, `bcom_load_image`, `bcom_set_initiator`, `bcom_enable`, and `bcom_disable`. Internal lifecycle is `bcom_engine_init`, `bcom_engine_cleanup`, `mpc52xx_bcom_probe`, and `mpc52xx_bcom_remove`.

Control flow: probe locates the SRAM node, initializes the SRAM allocator, allocates `bcom_engine`, maps BestComm registers, then initializes SRAM regions for task descriptor table, contexts, variables/increments, and the function descriptor table. `bcom_task_alloc` reserves an unused task number by marking TDT `stop`, allocates task metadata, maps task IRQ, and optionally allocates a BD ring from SRAM. `bcom_load_image` validates the image magic, allocates descriptor SRAM on first load or validates size on reload, clears variable/increment areas, and copies image sections into IO memory. Initiator setup patches both TCR and DRD initiator fields.

State and persistence: All runtime state is in `bcom_eng`, mapped SDMA registers, SRAM heaps, task descriptor table, task contexts, variable/inc areas, and allocated BD rings. No disk persistence. Driver uses `subsys_initcall` so built-in users can rely on early setup.

Dependencies/integration: OF platform matching, MPC52xx register definitions, BestComm private/public headers, SRAM allocator, IRQ mapping, and exported symbols consumed by ATA/FEC/GenBD helpers.

Risks: `bcom_eng` is a singleton global; task users assume core probe succeeded. Task reservation uses `tdt[].stop` as a marker. Reload size mismatch is rejected, but variable layout errors remain possible. Cleanup must stop all tasks before freeing SRAM.

Test signals: boot probe logs, SRAM region allocation, task allocation/free for each task family, microcode reload validation, initiator patching, IRQ mapping, module unload cleanup, and dependent ATA/FEC/PSC DMA operation.
