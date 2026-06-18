# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.h

Purpose: Tiny MMP private declaration header.

Important APIs/types/functions: Declares shared init/map helpers used by DT board files.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates MMP common code with `mmp-dt.c`, `mmp2-dt.c`, and `mmp3.c`.

Risks: Prototype drift causes build or boot-time init omissions.

Test signals: Compile all MMP machine descriptors.
