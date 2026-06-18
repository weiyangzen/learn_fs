# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconfig.c

## Purpose
`exconfig.c` implements AML dynamic table load and unload support for `LoadTable`, `Load`, and `Unload`-related execution paths. It turns table indices into DDB handles and integrates newly loaded tables into the namespace.

## Important APIs, Types, And Functions
Important functions are `acpi_ex_load_table_op`, `acpi_ex_load_op`, `acpi_ex_unload_table`, and private helpers `acpi_ex_add_table` and `acpi_ex_region_read`. It uses `struct acpi_table_header`, table manager APIs, namespace nodes, DDB local-reference objects, and executor store/region dispatch.

## Control Flow
`acpi_ex_load_table_op` creates an integer return object initialized to zero, finds a table by signature/OEM fields, resolves optional root and parameter paths, loads the table under the chosen parent, creates a table-reference DDB handle, initializes namespace objects, optionally stores caller parameter data, then returns all-ones success. `acpi_ex_load_op` accepts a system-memory operation region or a buffer/resolved field. For regions, it evaluates region arguments, reads the ACPI header bytewise through the region handler, validates length, allocates a copy, and reads the full table through operation-region dispatch. For buffers, it validates header length and copies the table bytes. It then installs and loads the table from the internal buffer, initializes namespace objects, and sets the target integer to all ones. `acpi_ex_unload_table` validates a DDB handle but currently emits warnings and returns not implemented through table unload support behavior.

## State And Persistence
Dynamic loads update ACPICA table manager state and namespace contents. DDB handles are local-reference operand objects flagged `AOPOBJ_DATA_VALID` with the table index in `reference.value`. The loaded table buffer is copied so later AML buffer/region changes do not affect table manager state.

## Dependencies And Integration Points
The code integrates the interpreter lock with table manager locks by exiting/re-entering the interpreter around table operations and namespace initialization. Region-backed loads depend on address-space handlers and field dispatch.

## Risks
Dynamic table load executes namespace initialization and can run AML side effects. Region reads are bytewise and handler-dependent, so malformed or slow handlers affect load behavior. Load failure after table insertion can leave partially initialized table-manager state if downstream cleanup is incomplete. Unload is intentionally unsupported, so AML relying on it will fail.

## Test Signals
Tests should cover table-not-found returning integer zero, successful `LoadTable` with root/parameter paths, bad path failures, region-backed length validation, buffer limit checks, copied-table lifetime, interpreter lock release around table manager calls, and DDB handle validation for unload.
