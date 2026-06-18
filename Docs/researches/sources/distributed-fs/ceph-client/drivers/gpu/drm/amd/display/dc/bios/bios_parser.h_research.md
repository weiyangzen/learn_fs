# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.h

Purpose: declares the public constructor for the legacy ATOMBIOS parser implementation.

Important API: `struct dc_bios *bios_parser_create(struct bp_init_data *init, enum dce_version dce_version);` returns a `dc_bios` interface on success or `NULL` when the ROM is unsupported or invalid. The implementation lives in `bios_parser.c`.

Control flow and integration: callers do not include this as the primary API; `bios_parser_interface.c` uses it as a fallback after the atomfirmware parser fails. The header intentionally exposes no internals; private layout is in `bios_parser_types_internal.h`.

State, dependencies, risks, and tests: state is owned by the returned `dc_bios` and destroyed through the function table, not this header. The main dependency risk is forward declarations being supplied by including translation units. Test signals are compile coverage and parser-selection tests that confirm fallback creation calls this constructor for legacy ROM revisions.
