# sources/distributed-fs/ceph-client/include/linux/nls.h

Purpose: Declares the kernel native language support charset table interface and Unicode conversion helpers.

Important APIs, types, and functions: Key types are `wchar_t`, `unicode_t`, `struct nls_table`, and `enum utf16_endian`. APIs register/unregister/load/unload NLS tables, load default charset, convert UTF-8/UTF-16/UTF-32, and case-fold or compare strings through table callbacks. Detected source surface: 109 lines; includes `linux/init.h`; macros `MAX_WCHAR_T`, `MODULE_ALIAS_NLS`, `NLS_MAX_CHARSET_SIZE`, `_LINUX_NLS_H`, `register_nls`; structs `module`, `nls_table`; enums `utf16_endian`; typedefs `unicode_t`, `wchar_t`; function-like declarations/helpers `__register_nls`, `nls_nullsize`, `nls_strnicmp`, `nls_tolower`, `nls_toupper`, `unload_nls`, `unregister_nls`, `utf16s_to_utf8s`, `utf32_to_utf8`, `utf8_to_utf32`, `utf8s_to_utf16s`.

Control flow: Filesystems load an NLS table by charset name, call character conversion and case maps while parsing names, and unload the table when no longer needed.

State and persistence behavior: Registered charset tables are module-backed global state; loaded table references persist for filesystem mount lifetime.

Dependencies and integration points: Depends on init/module support and character conversion implementations. Used by FAT, ISO9660, CIFS, and other filename-encoding consumers.

Risks and test signals: Risks are module reference leaks, invalid multibyte handling, and case-fold mismatches. Test charset load/unload, invalid UTF sequences, UTF-16 endian variants, and case-insensitive lookups.
