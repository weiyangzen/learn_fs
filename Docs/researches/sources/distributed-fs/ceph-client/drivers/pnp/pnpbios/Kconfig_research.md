<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig

Purpose: Build configuration for legacy x86 32-bit PnP BIOS backend and optional proc interface.

Important APIs/types/functions: `PNPBIOS` depends on `ISA && X86_32` and defaults off. `PNPBIOS_PROC_FS` depends on `PNPBIOS && PROC_FS`.

Control flow/state: build-time only.

Dependencies/integration: exposes legacy PnP BIOS service access; help warns ACPI supersedes it and proc writes can be dangerous.

Risks: PnP BIOS calls can fault on buggy firmware and are intentionally disabled by default.

Test signals: x86_32 ISA build with and without procfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig -->
