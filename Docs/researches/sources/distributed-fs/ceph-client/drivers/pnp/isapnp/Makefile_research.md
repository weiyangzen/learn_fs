<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile

Purpose: Kbuild rules for the ISA PnP backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o compat.o`, adding `proc.o` when `CONFIG_PROC_FS` is enabled.

Control flow/state: build-time only.

Dependencies/integration: links ISA PnP protocol, old API compatibility, and optional `/proc/bus/isapnp`.

Risks: optional proc interface changes externally visible debug/config surface.

Test signals: builds with and without `CONFIG_PROC_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile -->
