<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h

Purpose: declares SolutionEngine MR-SHPC PCMCIA window setup.

Important APIs/types/functions: `mrshpc_setup_windows()`.

Control flow: board PCMCIA setup calls this helper after MR-SHPC register mappings are available.

State and persistence: state lives in MR-SHPC memory and I/O window registers, not the header.

Dependencies/integration: integrates with SE board headers and PCMCIA/CF resource setup.

Risks: incorrect window setup prevents card detection or maps attribute/common memory incorrectly.

Test signals: boot SE PCMCIA-capable boards and test CF/card insertion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h -->
