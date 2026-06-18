<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h

Purpose: Private header for PnP ACPI resource parsing/encoding APIs.

Important APIs/types/functions: declares `pnpacpi_parse_allocated_resource()`, `pnpacpi_parse_resource_option_data()`, `pnpacpi_encode_resources()`, and `pnpacpi_build_resource_template()`.

Control flow/state: no runtime logic.

Dependencies/integration: includes ACPI and PnP public headers; shared between `core.c` and `rsparser.c`.

Risks: signature changes must be coordinated across ACPI backend files.

Test signals: compile coverage of core/parser integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h -->
