# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal2.h

Purpose: defines private data structures for the atomfirmware parser.

Important types: `struct atom_data_revision` mirrors the legacy helper. `struct object_info_table` stores revision plus a union of `display_object_info_table_v1_4 *` and `display_object_info_table_v1_5 *`. `enum spread_spectrum_id` keeps the same legacy SS constants for compatibility. `struct bios_parser` embeds `struct dc_bios base`, atomfirmware display object table state, `atom_master_data_table_v2_1 *master_data_tbl`, helper pointers, command table dispatch, and `remap_device_tags`. `BP_FROM_DCB()` casts public callbacks back to the atomfirmware parser container.

Control flow and integration: included by `bios_parser2.c`, helper code, and command-table2 code. Its object-info union is the root of parser2’s repeated v1.4/v1.5 branch decisions.

State and persistence: defines the parser2 lifetime state allocated by `firmware_parser_create()` and freed by `firmware_parser_destroy()`. ROM pointers point into `dc_bios.base.bios`; derived info is stored separately on `base`.

Dependencies and risks: depends on `dc_bios_types.h`, `bios_parser_helper.h`, and atomfirmware type declarations from implementation units. Like the legacy internal header, it defines `struct bios_parser` and `struct atom_data_revision` names, so it is intended for separate parser2 translation units rather than shared inclusion with legacy internals. Misusing `BP_FROM_DCB()` with a legacy parser object would corrupt interpretation.

Test signals: compile coverage for parser2 and command-table2, constructor tests for display object table v1.4/v1.5, and callback tests proving parser2 function-table methods receive parser2-owned `dc_bios` objects.
