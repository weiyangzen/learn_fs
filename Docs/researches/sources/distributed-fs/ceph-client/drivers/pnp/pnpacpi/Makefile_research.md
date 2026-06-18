<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile

Purpose: Kbuild rules for PnP ACPI backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o` and `rsparser.o`.

Control flow/state: build-time only.

Dependencies/integration: links ACPI enumeration logic with ACPI resource parse/encode helpers.

Risks: omitting `rsparser.o` would compile enumeration but break get/set/resource-option support.

Test signals: compile with `CONFIG_PNPACPI=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile -->
