<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h

Purpose: defines Migor board pin/control register addresses and LCDC setup callback declaration.

Important APIs/types/functions: `PORT_MSELCRA`, `PORT_MSELCRB`, `BSC_CS*`, and `migor_lcdc_setup()`-style LCDC bus op prototype.

Control flow: board setup uses constants to configure bus/pin state and hands system bus ops to LCDC.

State and persistence: state is hardware register configuration done by board code.

Dependencies/integration: integrates with SuperH board setup, BSC, pinmux, and sh_mobile_lcdc.

Risks: wrong bus width/timing registers can break flash/LCD access early in boot.

Test signals: build Migor board support and test LCD plus external memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h -->
