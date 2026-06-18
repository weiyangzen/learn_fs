# sources/distributed-fs/ceph-client/drivers/acpi/nhlt.c

`nhlt.c` exports helpers for ACPI NHLT audio topology. It retrieves the global NHLT table, searches endpoints and format configurations, and derives PDM microphone counts from endpoint configuration.

Important APIs are `acpi_nhlt_get_gbl_table()`, `acpi_nhlt_put_gbl_table()`, `acpi_nhlt_endpoint_match()`, `acpi_nhlt_tb_find_endpoint()`, `acpi_nhlt_find_endpoint()`, `acpi_nhlt_endpoint_find_fmtcfg()`, `acpi_nhlt_tb_find_fmtcfg()`, `acpi_nhlt_find_fmtcfg()`, and `acpi_nhlt_endpoint_mic_count()`. The file stores `acpi_gbl_nhlt`, falling back to a static empty table if none exists.

Control flow is iterator-based: endpoint searches walk `for_each_nhlt_endpoint`, format searches walk each endpoint's format configs, and mic-count logic validates PDM endpoints, computes max channel count, checks mic-array capabilities, maps known array types to 2 or 4 microphones, and validates variable vendor arrays.

Dependencies include ACPICA table lookup, `<acpi/nhlt.h>` data structures and iterator macros, and audio drivers consuming exported symbols. Risks include global table lifecycle without local locking, current limitation to table index 0, bounds reliance on iterator macros, and vendor mic capability size validation. Test signals include missing NHLT fallback, endpoint wildcard matches, format lookups, non-PDM rejection, standard and vendor mic arrays, malformed capability sizes, and get/put lifecycle behavior.
