# sources/distributed-fs/ceph-client/drivers/base/test/property-entry-test.c

Purpose: this KUnit file validates the property-entry and software-node property API implemented by the device property/fwnode stack.

Important APIs, types, and functions: test cases are `pe_test_uints`, `pe_test_uint_arrays`, `pe_test_strings`, `pe_test_bool`, `pe_test_move_inline_u8`, `pe_test_move_inline_str`, and `pe_test_reference`. They use property macros such as `PROPERTY_ENTRY_U8`, `PROPERTY_ENTRY_U16_ARRAY`, `PROPERTY_ENTRY_STRING_ARRAY`, `PROPERTY_ENTRY_BOOL`, `PROPERTY_ENTRY_REF`, and `PROPERTY_ENTRY_REF_ARRAY`; fwnode APIs such as `fwnode_create_software_node`, `fwnode_property_read_*`, count helpers, and `fwnode_property_get_reference_args`; and software-node group registration.

Control flow: tests create software nodes with static property entries, read properties back through generic fwnode helpers, assert exact values and error behavior for missing or overlarge reads, then remove the software node. Copy tests call `property_entries_dup` and inspect `is_inline`, `value`, and `pointer` storage choices. Reference tests register two software nodes, create reference properties to them, resolve references with different argument counts and indexes, and unregister the group.

State and persistence: each test creates temporary software nodes and removes them before returning. Duplicated property entries are explicitly freed. Static referenced nodes exist for test duration and are registered as a group only inside the reference test.

Dependencies and integration points: this is the main local test signal for `drivers/base/swnode.c` property handling. It also exercises generic fwnode property readers and KUnit assertions.

Risks: tests intentionally rely on current element-count semantics, including counting a 64-bit property as four 16-bit elements and a 16-bit array as two 64-bit chunks when divisible. Inline-storage checks are sensitive to `struct property_entry` layout and copy policy. Reference tests must unregister on all successful paths to avoid contaminating later tests.

Test signals: the KUnit suite is `property-entry`. Passing tests signal correct scalar/array/string/bool read behavior, error returns for missing or overflowed properties, deep-copy behavior for inline and heap data, and software-node reference resolution.
