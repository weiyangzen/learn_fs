# sources/distributed-fs/ceph-client/scripts/insert-sys-cert.c

## Purpose
Patches a built `vmlinux` image by inserting an extra system certificate into the reserved `system_extra_cert` area and updating related size/used symbols.

## APIs, Control Flow, and State
The tool accepts `-b <vmlinux> -c <certfile> [-s <System.map>]`. It reads the certificate into memory, mmaps `vmlinux` read-write, validates ELF magic, host-matching ELF class, endianness, and section header range, then locates symbols either through `.symtab` or by translating System.map addresses into file offsets. It resolves `system_extra_cert`, `system_extra_cert_used`, and `system_certificate_list_size`, verifies the reserved area can hold the cert, avoids rewriting if identical, zero-fills unused space, adjusts certificate-list size by the delta, and writes the used byte count.

## Dependencies and Integration
It depends on ELF headers, `mmap(MAP_SHARED)`, writable build artifacts, optional System.map, and the kernel link reserving the three symbols. It integrates with certificate insertion flows after kernel image linking.

## Risks and Test Signals
Risks include host/target ELF class mismatch for cross builds, unchecked pointer arithmetic over malformed ELF files, symbol size inference from System.map, and mutating `vmlinux` in place. Test signals include symbol-resolution logs, rejection of oversized certs, idempotent reinsertion, boot-time trust of the inserted cert, and successful fallback when `.symtab` is absent.
