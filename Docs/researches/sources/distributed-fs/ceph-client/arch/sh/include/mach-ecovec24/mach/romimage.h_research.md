<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h

Purpose: implements an Ecovec24 ROM-image MMCIF progress indicator.

Important APIs/types/functions: `mmcif_update_progress()` writes board GPIO/port registers such as `HIZCRA` and `PGDR`.

Control flow: the hook toggles/updates board-visible progress state from early boot code.

State and persistence: state is direct hardware latch/GPIO output only.

Dependencies/integration: depends on early raw I/O helpers and Ecovec24 port register layout before full drivers exist.

Risks: raw register writes during early boot can conflict with later pinmux/GPIO setup if values drift.

Test signals: boot an Ecovec24 ROM image and verify progress indication and later GPIO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h -->
