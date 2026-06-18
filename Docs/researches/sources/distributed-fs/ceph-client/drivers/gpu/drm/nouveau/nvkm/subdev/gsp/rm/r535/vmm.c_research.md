# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/vmm.c

Purpose: wraps a hardware `nvkm_mmu_func` with R535 GSP-RM virtual address space promotion support. It creates and destroys RM VASpace objects for Nouveau VMMs and teaches RM about either Nouveau-owned page directories or RM-reserved server PDE ranges.

Important APIs: `r535_mmu_vaspace_new()` constructs a GSP client/device pair, allocates a `FERMI_VASPACE_A` object, and either sets external ownership or reserves/copies server RM PDEs. `r535_mmu_vaspace_del()` unsets external page directories when needed, frees the RM VAS object, destroys device/client wrappers, and releases reserved VMM space. `r535_mmu_promote_vmm()` promotes an existing VMM as external using handle `NVKM_RM_VASPACE`. `r535_mmu_new()` clones the hardware MMU function table and overrides `.promote_vmm`.

Control flow: VAS creation first calls `nvkm_gsp_client_device_ctor()`. It prepares `NV_VASPACE_ALLOCATION_PARAMETERS`, sets `index = GPU_NEW`, and sets `IS_EXTERNALLY_OWNED` for external VMMs. For internal RM-managed VAS, it reserves the fixed 512 MiB server range at 4 GiB with 512 MiB page coverage, walks the Nouveau page descriptor hierarchy, fills `NV90F1_CTRL_VASPACE_COPY_SERVER_RESERVED_PDES_PARAMS` with physical addresses/sizes/apertures/page shifts for each page-table level, and writes the control. For external VAS, it sends `NV0080_CTRL_DMA_SET_PAGE_DIRECTORY` with the root page-table address, entry count, aperture VIDMEM flag, and VAS handle.

State and persistence: `vmm->rm.client`, `vmm->rm.device`, and `vmm->rm.object` persist while the VMM is promoted. `vmm->rm.rsvd` persists only for internally owned VAS and is released on delete. `vmm->rm.external` tracks whether an unset-page-directory control is required before free.

Dependencies and integration: depends on Nouveau MMU/VMM internals, `nvhw/drf.h` bitfield helpers, `nvrm/vmm.h`, GSP RM client/device helpers, and RM alloc/control functions. Channel allocation later consumes `vmm->rm.object.handle` as `hVASpace`.

Risks: failures after client/device construction or VAS allocation can leave partial RM objects unless higher-level destructors run. The server-reserved VA address and size are asserted; any firmware policy change requires header/code update. Page table walking assumes a compatible descriptor chain and uses `pd->pt[0]->addr` at each level. External unbind failure is warned but deletion proceeds.

Test signals: create/destroy promoted VMMs, allocate channels against promoted VAS handles, test mappings around the 4 GiB reserved range, validate external VMM teardown sends unset-page-directory, and run workloads after VMM promotion without MMU faults.
