# sources/distributed-fs/ceph-client/include/linux/prmt.h

Purpose: exposes ACPI Platform Runtime Mechanism Table support to generic callers that need to discover and invoke PRM handlers by GUID.

Important APIs and types: under `CONFIG_ACPI_PRMT`, `init_prmt()` initializes PRMT handling, `acpi_prm_handler_available()` checks for a handler GUID, and `acpi_call_prm_handler()` invokes a handler with a parameter buffer. Without the config, the functions become no-ops or return `false`/`-EOPNOTSUPP`.

Control flow: ACPI initialization calls `init_prmt()`, then drivers or platform code can check availability before calling a runtime handler. The header enforces a graceful disabled path so callers can compile independent of PRMT support.

State and persistence: no state is defined here; parsed ACPI table data and handler metadata live in the ACPI PRMT implementation. Handler calls may affect firmware/platform runtime state.

Dependencies and integration points: depends on `linux/uuid.h`, ACPI PRMT table parsing, and firmware-provided handler GUIDs. It integrates ACPI firmware services with kernel drivers needing platform runtime operations.

Risks and test signals: risks include calling unavailable handlers, malformed parameter buffers, firmware side effects, and config-disabled behavior not being checked. Test ACPI PRMT discovery, GUID lookup, successful and failing handler calls, bad buffers, and builds without `CONFIG_ACPI_PRMT`.
