# sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.h

Purpose: shared interface between the CXL mock dispatcher and concrete CXL test topology provider.

Important APIs, types, and functions: defines `struct cxl_mock_ops`, a callback table with predicates and mock implementations for ACPI device detection, CEDT parsing, bridge/bus/port/device classification, ACPI integer/root lookup, decoder setup, CDAT parsing, dport lookup, HMAT cache size, hmem resource walking, and region intersection tests. Declares hmem init/exit and mock ops registration/SRCU accessors.

Control flow: `test/cxl.c` fills a `cxl_mock_ops` instance and registers it. `test/mock.c` wrapper functions retrieve it and call the relevant callback.

State and persistence: the ops structure includes a `list_head` so providers can be linked into the global registry. Actual callback state is owned by the provider module.

Dependencies and integration points: includes Linux list, ACPI, DAX, and CXL headers. It is a contract between `mock.c`, `mock_acpi.c`, and `cxl.c`.

Risks: changes to wrapped production function signatures require corresponding callback changes. Several callbacks are optional only by convention; wrappers often assume non-null methods when ops exists.

Test signals: compile-time agreement between all CXL test modules and successful wrapper dispatch.
