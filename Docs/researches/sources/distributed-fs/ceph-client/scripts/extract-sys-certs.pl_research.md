# sources/distributed-fs/ceph-client/scripts/extract-sys-certs.pl

Purpose: Extracts the built-in system certificate list from `vmlinux` into a keyring file.

Important APIs/functions: Parses `objdump -h` section rows into VMA/file-offset metadata, parses `nm` or optional System.map symbols, locates `__cert_list_start` and `system_certificate_list_size`, reads the list size from the image, validates section containment, then copies the certificate bytes to the output file.

Control flow: Validates either `<vmlinux> <keyring>` or `-s <System.map> <vmlinux> <keyring>`, builds section and symbol tables, falls back to System.map if `nm` has no symbols, verifies required symbols, finds the containing section, computes file offsets with `Math::BigInt`, reads bytes, and writes the keyring file.

State/persistence: Writes the output keyring file. Uses in-memory section and symbol tables.

Dependencies/integration: Perl, `Math::BigInt`, `Fcntl`, `objdump`, `nm`, and optionally System.map. Used in certificate extraction workflows where vmlinux contains key material.

Risks: Parses human-readable binutils output with regexes. Size is read as native unsigned long via `unpack 'L!'`, so cross-width/cross-endian assumptions matter. Output file is overwritten. Diagnostic messages go to stdout and stderr mixed through `die`.

Test signals: vmlinux with symbols, extract-vmlinux output plus System.map fallback, missing symbols, cert spanning a section boundary, 32/64-bit host width behavior, and short read/write failures.
