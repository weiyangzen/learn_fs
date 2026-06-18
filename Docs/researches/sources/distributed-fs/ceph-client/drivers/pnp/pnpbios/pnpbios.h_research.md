<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h

Purpose: Private definitions for the PnP BIOS backend: firmware status codes, event/message constants, flags, packed firmware structures, install structure layout, and internal function declarations.

Important APIs/types/functions: defines PnP/ESCD status constants, event/message values, `PNPBIOS_*` flags, `pnpbios_is_static/dynamic`, `PNPMODE_STATIC/DYNAMIC`, packed structs for node info, docking info, ISA config, ESCD info, BIOS node, and install structure. Declares BIOS wrappers, parser/encoder APIs, protocol globals, and proc hooks.

Control flow/state: no runtime flow, but packed layout is ABI-critical for firmware calls and resource node handling.

Dependencies/integration: shared by `bioscalls.c`, `core.c`, `proc.c`, and `rsparser.c`; depends on PnP public types.

Risks: packing or field changes would break firmware ABI. Inline no-op proc hooks must match enabled prototypes.

Test signals: compile with proc on/off, structure size/layout checks on x86_32, and wrapper signature compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h -->
