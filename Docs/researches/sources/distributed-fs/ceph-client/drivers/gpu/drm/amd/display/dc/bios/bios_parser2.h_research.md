# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.h

Purpose: declares the public constructor for the atomfirmware parser implementation.

Important API: `struct dc_bios *firmware_parser_create(struct bp_init_data *init, enum dce_version dce_version);` returns a `dc_bios` interface for atomfirmware ROMs or `NULL` when unsupported. The implementation lives in `bios_parser2.c`.

Control flow and integration: `bios_parser_interface.c` calls this constructor first, so this header is the preferred parser entry point for modern ASICs. Private parser state is intentionally hidden in `bios_parser_types_internal2.h`.

State, dependencies, risks, and tests: the header owns no state; lifecycle is through the returned function table. Risk is mainly ABI/compile drift if `bp_init_data` or `dce_version` declarations are not visible to includers. Test signals are compile coverage and parser-selection tests proving modern ROMs use this constructor before legacy fallback.
