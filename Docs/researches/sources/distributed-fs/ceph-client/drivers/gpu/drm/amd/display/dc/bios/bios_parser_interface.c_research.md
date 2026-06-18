# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_interface.c

Purpose: provides the single parser factory/destructor API used by the rest of Display Core.

Important functions: `dal_bios_parser_create()` first calls `firmware_parser_create()` for atomfirmware ROMs, then falls back to `bios_parser_create()` for older ATOMBIOS ROMs. `dal_bios_parser_destroy()` delegates destruction through `bios->funcs->bios_parser_destroy`.

Control flow: parser selection is optimistic for the newer parser. A `NULL` return from parser2 is not fatal; it is the signal to try the legacy parser. Destruction assumes the caller passes a non-null pointer to a valid `dc_bios`.

State and persistence: no own state. It returns whichever concrete parser owns the allocated memory and function table.

Dependencies and integration points: depends on both parser headers, logging/services, and the public BIOS parser interface include. This file is the boundary that hides parser-generation differences from higher Display Core code.

Risks: no null checks in `dal_bios_parser_destroy()` before dereferencing `*dcb`, so callers must avoid destroying null/uninitialized parser handles. Parser selection relies on constructors cleanly returning `NULL` for unsupported ROMs without side effects.

Test signals: create tests with mock ROM headers for parser2 success, parser2 fail plus legacy success, and both fail. Destruction tests should verify the concrete parser destructor nulls the caller pointer.
