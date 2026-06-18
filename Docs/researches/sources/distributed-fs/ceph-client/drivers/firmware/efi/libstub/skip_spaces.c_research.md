
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/skip_spaces.c

Purpose: supplies the small `skip_spaces()` helper for command-line parsing in the EFI stub.

Important APIs/types/functions: exports `skip_spaces(const char *str)`.

Control flow: advances the pointer while `isspace(*str)` is true and returns a writable `char *` cast of the resulting position.

State and persistence behavior: no state.

Dependencies and integration points: depends on Linux ctype/string types and is used by `efi_parse_options()` and other parser-style code.

Risks and test signals: behavior follows C `isspace()` on bytes; callers must pass NUL-terminated strings. Test signals include leading spaces, tabs/newlines, empty strings, and no-leading-space command lines.
