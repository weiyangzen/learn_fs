<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h

Purpose: This minimal header preserves the platform-data type for the Renesas SuperH HSPI driver.

Important APIs/types/functions: It defines an empty `struct sh_hspi_info`, leaving room for board data without any current fields.

Control flow: No control flow is declared here. Platform code may still use the type as a marker.

State and persistence: No state.

Dependencies/integration: Integrates only by type name with legacy SH HSPI platform data.

Risks and test signals: Risks are limited to compatibility and dead field assumptions. Test signal is compile coverage for any HSPI board files using `sh_hspi_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/sh_hspi.h -->
