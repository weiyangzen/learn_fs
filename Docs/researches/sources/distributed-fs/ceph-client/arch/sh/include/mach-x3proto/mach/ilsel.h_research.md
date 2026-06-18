<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h

Purpose: defines the X3PROTO interrupt line selector interface constants.

Important APIs/types/functions: ILSEL-related include guard and selector declarations/macros in the header.

Control flow: board IRQ setup programs line selectors before registering interrupt sources.

State and persistence: state is selector register contents in board hardware.

Dependencies/integration: integrates with X3PROTO FPGA/baseboard interrupt routing.

Risks: wrong selector mapping makes valid devices appear interrupt-dead.

Test signals: test every routed baseboard interrupt source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h -->
