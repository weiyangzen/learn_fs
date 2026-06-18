## sources/distributed-fs/ceph-client/drivers/acpi/apei/apei-base.c

Purpose: `apei-base.c` implements shared APEI infrastructure for ERST/EINJ action-table interpretation, Generic Address Register access, APEI resource reservation, debugfs setup, architecture hooks, and WHEA `_OSC` negotiation.

Important APIs and functions: `apei_exec_ctx_init`, `__apei_exec_run`, `apei_exec_read_register`, `apei_exec_read_register_value`, `apei_exec_write_register`, `apei_exec_write_register_value`, `apei_exec_noop`, `apei_exec_pre_map_gars`, `apei_exec_post_unmap_gars`, and `apei_exec_collect_resources` operate on `struct apei_exec_context`. Resource APIs include `apei_resources_add`, `apei_resources_sub`, `apei_resources_request`, `apei_resources_release`, and `apei_resources_fini`. GAR APIs include `apei_map_generic_address`, `apei_read`, and `apei_write`. `apei_get_debugfs_dir` lazily creates `/sys/kernel/debug/apei`; `apei_osc_setup` runs WHEA `_OSC`.

Control flow: the interpreter scans action-table entries matching an action, validates instruction indexes, invokes instruction handlers, supports handler-directed jumps through `ctx->ip`, and treats missing optional actions as success. Pre-map and resource collection iterate every entry and act only on instruction types flagged `APEI_EXEC_INS_ACCESS_REGISTER`.

State and persistence: global `apei_resources_all` tracks all requested APEI I/O memory and I/O port ranges. Resource lists merge overlapping intervals, subtract already requested, NVS, and arch-filtered regions, then request/release kernel resources. A static debugfs dentry persists after first creation.

Dependencies and integration: the file depends on ACPI GAS accessors, ACPI NVS iteration, resource reservation APIs, debugfs, CPER/WHEA concepts, and weak architecture hooks. ERST, EINJ, GHES, and BERT use this common layer.

Risks: resource interval math must handle overlaps/splits correctly. GAR validation rejects zero addresses, invalid access widths, bad bit ranges, and unsupported address spaces; firmware bugs are common. Action-table loops with jumps must avoid unintended rewinds.

Test signals: invalid instruction indexes, optional missing actions, jump handlers, pre-map rollback on failure, overlapping resource merge/subtract/split, NVS/arch exclusion, GAR read/write for memory and I/O, invalid GAS fields, and `_OSC` failure/success are key.
