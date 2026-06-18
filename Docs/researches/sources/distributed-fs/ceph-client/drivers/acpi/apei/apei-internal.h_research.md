## sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-internal.h

Purpose: `apei-internal.h` declares internal APEI execution, resource, debugfs, CPER, `_OSC`, and EINJ helper interfaces shared by APEI translation units.

Important APIs and types: `struct apei_exec_context` holds interpreter instruction pointer, value registers, base registers, instruction table, action table pointer, and entry counts. `struct apei_exec_ins_type` pairs flags with instruction handlers, and `APEI_EXEC_INS_ACCESS_REGISTER` marks register-accessing instructions. Inline helpers set/get interpreter input/output and wrap `__apei_exec_run` for required or optional actions. Resource helpers define `struct apei_resources` with `iomem` and `ioport` lists plus init/fini/add/sub/request/release prototypes. `cper_estatus_len` computes CPER generic status length using raw data offset/length if present. EINJ declarations cover base and CXL injection paths and validation.

Control flow: the header itself has only inlines. They map the public internal pattern: initialize context, set input, run an action, read output, and manage resources around tables.

State and dependencies: no storage is defined here except inline behavior. It depends on Linux ACPI types, list heads, debugfs forward declarations, CPER structures, and conditional fallback definitions for newer CXL EINJ bits.

Integration points: `apei-base.c`, `bert.c`, HEST/GHES/ERST/EINJ modules, and CXL EINJ support include this header to share contracts without exporting them outside the APEI implementation boundary.

Risks: structure field layout and helper semantics must stay synchronized with action-table interpreter code. `cper_estatus_len` trusts firmware-provided lengths and must be paired with validation before walking records.

Test signals: compile coverage for every APEI object, optional-action wrapper behavior, resource init producing empty lists, CPER status length with and without raw data, and availability of fallback CXL EINJ bit definitions are relevant.
