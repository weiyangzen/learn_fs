# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fbsr.h

Purpose: defines the R535 framebuffer suspend/resume memory-list and control payloads. These structures let Nouveau describe system/FB memory regions that RM should preserve across suspend or runtime power transitions.

Important types: `rpc_alloc_memory_v13_01` allocates memory-list objects with client/device/memory handles, class, flags, length, page count, and embedded `pte_desc` entries. `NV2080_CTRL_INTERNAL_FBSR_INIT_PARAMS` initializes FBSR with type, region count, client/sysmem handles, GSP FB allocation offset, and GC-off state. `NV2080_CTRL_INTERNAL_FBSR_SEND_REGION_INFO_PARAMS` sends per-region vidmem/sysmem offsets and size. Constants define `NV01_MEMORY_LIST_FBMEM`, `NV01_MEMORY_LIST_SYSTEM`, `FBSR_TYPE_DMA`, and `NVOS02` memory flags.

Control flow and state: R535 and R570 FBSR code build memory list objects over scatter-gather system memory, initialize RM FBSR, and send region mappings. Persistent state includes the allocated system memory backing suspend data and RM memory object handles until resume cleanup.

Dependencies and integration: included by FBSR implementations and tied to `r535_gsp_fini()` suspend handling. It also intersects BAR/instmem state because resume must restore page tables before normal BAR2 use.

Risks and tests: size and page-count mismatches can corrupt preserved VRAM or fail resume. The flexible `pte_desc` layout is sensitive to allocation sizing and alignment. Tests should cover system suspend/resume, runtime suspend/resume, high VRAM allocation pressure, and verification that channels survive resume without forced reset.
