# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/bar.h

Purpose: defines the R535 RPC payload for updating RM-managed BAR page directory entries.

Important types: `NV_RPC_UPDATE_PDE_BAR_TYPE` selects BAR1, BAR2, or invalid. `UpdateBarPde_v15_00` carries the target BAR type, a 64-bit entry value, and entry level shift. `rpc_update_bar_pde_v15_00` wraps that structure for the `UPDATE_BAR_PDE` RPC function.

Control flow and state: no code is present. State represented by this ABI is the current RM view of BAR page directory entries, usually synchronized with Nouveau's BAR/MMU setup.

Dependencies and integration: consumed by BAR update code outside this work item and tied to `NV_VGPU_MSG_FUNCTION_UPDATE_BAR_PDE` from `rpcfn.h`. It depends on `nvrm/nvtypes.h` for aligned 64-bit fields.

Risks and tests: incorrect BAR type or alignment can break BAR1/BAR2 access and therefore instance memory, VRAM mappings, and resume restoration. Test signals include BAR1/BAR2 mapping operations, page table updates, and suspend/resume paths that depend on BAR accessibility.
