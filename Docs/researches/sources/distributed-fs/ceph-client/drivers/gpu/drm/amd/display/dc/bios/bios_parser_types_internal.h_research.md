# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal.h

Purpose: defines private data structures for the legacy ATOMBIOS parser.

Important types: `struct atom_data_revision` stores major/minor table revisions. `struct object_info_table` stores revision plus a union of `ATOM_OBJECT_HEADER *v1_1` and `ATOM_OBJECT_HEADER_V3 *v1_3`. `enum spread_spectrum_id` defines legacy SS info table IDs. `struct bios_parser` embeds `struct dc_bios base`, object-info state, master data table pointer, helper pointers, command table dispatch, and `remap_device_tags`. `BP_FROM_DCB()` converts the public `dc_bios` pointer back to this private container.

Control flow and integration: included by `bios_parser.c`, `bios_parser_helper.c`, and command-table code that needs parser internals. The embedded `dc_bios` makes concrete parser memory compatible with the public interface and function-table callbacks.

State and persistence: this header defines all long-lived parser state for the legacy parser: ROM table pointers, offsets, command dispatch, and helper selection. The actual allocation/free path is in `bios_parser.c`.

Dependencies and risks: depends on `dc_bios_types.h` and `bios_parser_helper.h`; transitive ATOM types must be visible in implementation units. Because `struct bios_parser` has the same tag name as parser2’s private type, these internal headers must not be included together in one translation unit in a way that conflicts. Macro misuse on a non-legacy `dc_bios` would reinterpret memory incorrectly.

Test signals: compile coverage for every legacy parser and command-table translation unit, plus lifecycle tests that ensure `BP_FROM_DCB()` callbacks operate on objects allocated by `bios_parser_create()`.
