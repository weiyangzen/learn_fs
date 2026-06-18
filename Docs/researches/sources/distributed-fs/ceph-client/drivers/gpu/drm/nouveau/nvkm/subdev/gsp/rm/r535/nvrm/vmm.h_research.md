# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/vmm.h

Purpose: defines R535 virtual-address-space allocation and page-directory control ABI structures.

Important definitions: `FERMI_VASPACE_A` is the VAS class. `NV_VASPACE_ALLOCATION_PARAMETERS` carries index, flags, VA size/range, big page size, and base. `NV_VASPACE_ALLOCATION_FLAGS_IS_EXTERNALLY_OWNED` marks a Nouveau-owned/external VAS. `SPLIT_VAS_SERVER_RM_MANAGED_VA_START` and `_SIZE` define the 4 GiB plus 512 MiB reserved server-RM window. `NV90F1_CTRL_VASPACE_COPY_SERVER_RESERVED_PDES_PARAMS` describes page levels to copy for RM-reserved VA space. `NV0080_CTRL_DMA_SET_PAGE_DIRECTORY_PARAMS` and `UNSET_PAGE_DIRECTORY_PARAMS` bind or unbind external page directories to a VAS.

Control flow and state: `vmm.c` allocates RM VAS objects with this payload, either sets an external page directory for Nouveau-owned VMMs or reserves/copies RM-managed PDEs for internally owned ones. State persists in `vmm->rm.object`, `vmm->rm.device/client`, `vmm->rm.rsvd`, and `vmm->rm.external`.

Dependencies and integration: included by R535 VMM code and tied to MMU promotion, BAR/VMM page table data, and RM control helpers. Uses bitfield macros at call sites for page-directory aperture flags.

Risks and tests: page-level descriptions must reflect Nouveau's actual page table hierarchy and physical addresses. The reserved VA range is asserted in code, so mismatch breaks VAS creation. Tests should create/destroy external and internal VAS objects, bind channels to VAS, and exercise mappings around the reserved range.
