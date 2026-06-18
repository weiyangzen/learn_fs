# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/d71/d71_dev.h

Purpose: declares D71-private device and pipeline structures plus D71 backend entry points.

Important APIs/types/functions: `struct d71_pipeline` embeds `struct komeda_pipeline` and stores LPU/CU/DOU MMIO bases plus DOU forward-transform coefficient base. `struct d71_dev` stores parent `komeda_dev`, block/pipeline/rich-layer counts, max dimensions, dual-link/TBU capability bits, GCU/global coefficient/PERIPH MMIO bases, and D71 pipeline pointers. Public declarations include `d71_pipeline_funcs`, `d71_probe_block()`, `d71_read_block_header()`, and `d71_dump()`. `to_d71_pipeline()` converts generic to chip-specific pipeline.

Control flow: created by `d71_enum_resources()`, filled during block probing, and consumed by D71 component update/IRQ/flush/debug paths.

State and persistence: all fields are runtime hardware-discovery state. The structures persist for the lifetime of `komeda_dev` and are freed by D71 cleanup.

Dependencies/integration: includes `komeda_dev.h`, `komeda_pipeline.h`, and `d71_regs.h`. It is the bridge between generic Komeda core and D71-specific registers.

Risks: array limits (`D71_MAX_PIPELINE`, `D71_MAX_GLB_SCL_COEFF`) must match hardware probing. Null sub-block pointers cause crashes in IRQ/update paths if block enumeration is incomplete. Test signals: probe logs, debugfs register dump, block-header fuzz/error handling, and multi-pipeline/dual-link hardware validation.
