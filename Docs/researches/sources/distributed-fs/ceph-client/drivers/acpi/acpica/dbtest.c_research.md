# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c

### Purpose
`dbtest.c` implements invasive debugger self-tests for namespace data objects and predefined-name evaluation. It installs helper AML methods that read and write arbitrary namespace objects through the interpreter so the tests exercise normal AML semantics instead of directly poking C structures.

### Important APIs, Types, And Functions
The command entry is `acpi_db_execute_test`, with subcommands `OBJECTS` and `PREDEFINED`. Key helpers include `acpi_db_test_all_objects`, `acpi_db_test_one_object`, typed tests for integer/buffer/string/package/field objects, `acpi_db_read_from_object`, `acpi_db_write_to_object`, `acpi_db_evaluate_all_predefined_names`, and `acpi_db_evaluate_one_predefined_name`. Static AML byte arrays define `\_T98` read and `\_T99` write helper methods.

### Control Flow
`OBJECTS` installs the read/write methods once, caches their handles, walks the namespace, maps supported object kinds to integer/string/buffer/package/field test families, reads original values, writes a synthetic value, reads back for comparison, restores the original, and verifies restoration. Field-unit tests directly acquire interpreter and namespace mutexes, read the field, write the same value back, then release locks. `PREDEFINED` walks predefined names, constructs default arguments based on predefined metadata, evaluates each object, and optionally stops at a count limit.

### State, Persistence, And Dependencies
The file persists `read_handle` and `write_handle` and installs debugger SSDT methods into the namespace. It temporarily mutates namespace data objects, field units, and operation-region-backed state. It depends on public method installation/evaluation APIs, namespace walking, predefined metadata, field I/O helpers, and interpreter/namespace mutexes.

### Integration Points
The tests validate object behavior implemented across namespace, interpreter, region, and field subsystems. They also overlap with `dbmethod.c` batch predefined evaluation but use spec-derived argument types instead of only integer defaults.

### Risks
This is intentionally destructive if restoration fails or firmware has side-effectful fields. Writing `0xFF` buffers, replacement strings, or max-width integers to fields can affect hardware-backed system memory, I/O, or PCI config regions. Unsupported spaces are skipped, but supported spaces still need care. Helper AML methods remain installed for the debugger session.

### Test Signals
Expected output is per-object type/name, length/value summaries, no mismatch messages after write/read/restore, field-unit tests limited to supported address spaces, successful helper method installation, predefined-name evaluations returning statuses rather than crashing, and no unreleased returned external-object buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbtest.c -->
