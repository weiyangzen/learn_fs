<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c

## Purpose
Adapts GF100 BAR handling for GSP-RM ownership, including BAR1/BAR2 page-directory handoff and BAR2 flush behavior.

## Important APIs, Types, And Functions
Defines `r535_bar_flush`, `r535_bar_bar2_update_pde`, BAR1/BAR2 init/fini/wait callbacks, `r535_bar_dtor`, and `r535_bar_new_`.

## Control Flow
BAR2 init reads Nouveau's BAR2 PDB entry, sends it to RM with `UPDATE_BAR_PDE`, records RM BAR2 PDB state in the VMM, maps a zero VRAM page as a flush target, and switches flushes to BAR2. BAR2 fini restores physical-mode flushing and clears the RM PDE. BAR1 init replaces the VMM root page directory memory with RM-provided BAR1 PDB memory. Constructor wraps a hardware BAR function table and ioremaps physical BAR2 for early/resume flushing.

## State And Persistence
Persists BAR function table, `flushBAR2`, `flushBAR2PhysMode`, `flushFBZero`, BAR1/BAR2 VMM page-directory memory, and `bar2` state. RM also stores BAR PDE state.

## Dependencies And Integration Points
Depends on GF100 BAR code, RAM wrapping, VMM page tables, GSP RPC control, framebuffer memory, and device resource mapping.

## Risks And Edge Cases
BAR2 flush is needed before BAR2 page tables are restored on resume. Failed zero-page mapping or PDE update is warned. Incorrect PDB handoff breaks CPU/GPU memory mappings.

## Test Signals
Successful BAR init/fini, no BAR2 flush faults across resume, valid BAR1/BAR2 mappings, and no `UPDATE_BAR_PDE` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c -->
