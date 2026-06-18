# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsutils.c

Purpose: provides helper functions for ACPICA resource conversion and namespace method execution. It handles bitmasks, endian/alignment-safe data movement, AML resource headers, optional resource sources, method evaluation for resource-producing methods, and `_SRS` invocation.

Important APIs, types, and functions: `acpi_rs_decode_bitmask()`, `acpi_rs_encode_bitmask()`, `acpi_rs_move_data()`, `acpi_rs_set_resource_length()`, `acpi_rs_set_resource_header()`, `acpi_rs_get_resource_source()`, `acpi_rs_set_resource_source()`, `acpi_rs_get_prt_method_data()`, `acpi_rs_get_crs_method_data()`, `acpi_rs_get_prs_method_data()`, `acpi_rs_get_aei_method_data()`, `acpi_rs_get_method_data()`, and `acpi_rs_set_srs_method_data()`.

Control flow: bitmask helpers convert IRQ/DMA masks to lists and back. `acpi_rs_move_data()` uses raw `memcpy` for byte moves and ACPICA move macros for 16/32/64-bit transfers to handle alignment/endian constraints. Header helpers write small-vs-large descriptor lengths. Resource-source get detects optional source data by comparing total length with the minimum descriptor length, copies index and null-terminated string, and rounds storage to native-word alignment; set appends index/string only when string length is nonzero. Method helpers evaluate `_PRT`, `_CRS`, `_PRS`, `_AEI`, or a named resource method, convert returned objects, release operand references, and for `_SRS` convert the input resource list to an AML buffer object before calling `acpi_ns_evaluate()`.

State and persistence: no durable state; it allocates temporary evaluation info and buffers, attaches buffers to operand objects, and releases references after method execution.

Dependencies and integration points: bridges resource conversion with ACPICA namespace/evaluator internals (`acpi_ut_evaluate_object`, `acpi_ns_evaluate`, operand objects, namespace nodes). Public APIs in `rsxface.c` delegate most method work here.

Risks and test signals: resource-source length math and `_SRS` buffer ownership are key risks. `acpi_rs_encode_bitmask()` assumes list values fit the target mask width. Tests should cover resource source absent/present strings, native alignment, endian-safe moves, all method helpers' object-type validation, reference cleanup on failures, and `_SRS` failure paths after AML buffer allocation.
