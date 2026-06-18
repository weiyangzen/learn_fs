<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile

Purpose: Kbuild rules for PnP BIOS backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o bioscalls.o rsparser.o`, optionally adding `proc.o`.

Control flow/state: build-time only.

Dependencies/integration: links firmware call thunking, PnP protocol enumeration, resource parser, and optional proc files.

Risks: object omission breaks either BIOS service calls or resource translation.

Test signals: compile `CONFIG_PNPBIOS=y` with `CONFIG_PNPBIOS_PROC_FS` on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile -->
