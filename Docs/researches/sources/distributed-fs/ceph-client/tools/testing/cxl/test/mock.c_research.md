# sources/distributed-fs/ceph-client/tools/testing/cxl/test/mock.c

Purpose: central wrapper dispatch module that lets CXL tests interpose selected ACPI, CXL, nvdimm, hmem, and region APIs with mock behavior.

Important APIs, types, and functions: maintains an SRCU-protected global `mock` list of `struct cxl_mock_ops`. Exports `register_cxl_mock_ops()`, `unregister_cxl_mock_ops()`, `get_cxl_mock_ops()`, and `put_cxl_mock_ops()`. Defines many `__wrap_*` functions: `is_acpi_device_node`, `acpi_table_parse_cedt`, `acpi_evaluate_integer`, `hmat_get_extended_linear_cache_size`, `acpi_pci_find_root`, `nvdimm_bus_register`, CXL decoder/dport/CDAT/media-ready helpers, `region_intersects`, `region_intersects_soft_reserve`, and `walk_hmem_resources`.

Control flow: wrapped functions acquire the current ops pointer with SRCU, decide whether the object belongs to the mock topology using ops predicates, call the mock implementation when applicable, otherwise call the real function, then release SRCU. Some wrappers augment real behavior, such as setting nvdimm provider name to `cxl_test` for mock parents or converting RCH dport creation into generic dport creation plus RCH metadata.

State and persistence: global list currently returns the first registered ops provider. SRCU protects readers across unregister. The module itself holds no per-device state.

Dependencies and integration points: requires top-level Kbuild linker `--wrap` flags so calls resolve to these functions. It imports ACPI and CXL namespaces and depends on CXL core, ACPI, PCI, hmem, libnvdimm, and resource APIs. `test/cxl.c` registers the concrete ops.

Risks: only one ops provider is effectively used despite list structure. Wrapper signatures must exactly track wrapped functions. Several wrappers assume object relationships, e.g. `dev->parent->parent` in nvdimm bus registration and memdev parent lookup in CDAT parsing. Missing fallback or wrong mock predicate can redirect real devices to test behavior or vice versa.

Test signals: loading `cxl_mock` plus `cxl_test` should cause production CXL drivers to consume mock CEDT/topology data. Removing ops should synchronize without use-after-free. Real paths should still fall back when devices are not mock-owned.
