## sources/distributed-fs/ceph-client/tools/lib/bpf/zip.h

Purpose: Declares the minimal libbpf ZIP reader API.

Important APIs/types: Opaque `struct zip_archive`; `struct zip_entry` with compression method, non-NUL entry name/length, data pointer/length, and data offset; lifecycle functions `zip_archive_open()`, `zip_archive_close()`, and lookup `zip_archive_find_entry()`.

Control flow: Callers open an archive, find entries by exact name, then close the archive after using returned data pointers.

State/persistence: Entry pointers are borrowed from the archive mapping and are not independently owned.

Dependencies/integration: Includes Linux integer types and pairs with `zip.c`. Comments document unsupported features.

Risks: Header comment says open returns NULL on error, while implementation returns `ERR_PTR()`. Callers must follow implementation/libbpf error-pointer conventions or risk dereferencing error values. Entry names are explicitly not NUL-terminated.

Test signals: Compile tests should validate callers use `IS_ERR`/`PTR_ERR`; API tests should check non-NUL names and compression handling.
