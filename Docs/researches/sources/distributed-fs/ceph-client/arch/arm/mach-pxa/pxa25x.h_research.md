<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h

Purpose: umbrella header for PXA25x board and SoC code.

Important contents: includes address map, PXA2xx registers, PXA25x MFP macros, and IRQ definitions.

Control flow and integration: board files such as Gumstix and AM200 include this to gain SoC register and pin definitions.

State and persistence: none.

Dependencies: depends on included headers.

Risks and test signals: compile coverage validates include ordering and macro availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h -->
