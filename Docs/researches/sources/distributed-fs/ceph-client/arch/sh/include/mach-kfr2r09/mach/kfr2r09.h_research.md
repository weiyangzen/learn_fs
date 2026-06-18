<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h

Purpose: declares KFR2R09 LCDC system-bus callbacks.

Important APIs/types/functions: `kfr2r09_lcdc_setup()`/teardown-style prototypes taking `sh_mobile_lcdc_sys_bus_ops`.

Control flow: board LCD setup code provides bus operations to the LCDC driver through these declarations.

State and persistence: no persistent state in the header; LCD controller state is managed by board/display code.

Dependencies/integration: depends on `video/sh_mobile_lcdc.h` style system bus operations.

Risks: prototype drift breaks board display bring-up at compile time or through wrong callbacks.

Test signals: build KFR2R09 display support and test panel enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h -->
