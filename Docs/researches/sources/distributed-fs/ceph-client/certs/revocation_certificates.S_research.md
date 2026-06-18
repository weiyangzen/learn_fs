<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/revocation_certificates.S -->
# sources/distributed-fs/ceph-client/certs/revocation_certificates.S

## Purpose

`revocation_certificates.S` embeds the generated `certs/x509_revocation_list` binary blob into the kernel image and exports its start pointer and size for revocation-list loading.

## Important APIs, Types, And Functions

It defines global symbols `revocation_certificate_list` and `revocation_certificate_list_size`, with internal labels `__revocation_list_start` and `__revocation_list_end`. It uses `.incbin`, `.align`, and either `.quad` or `.long` depending on `CONFIG_64BIT`.

## Control Flow

There is no runtime control flow. The assembler emits init read-only data; `blacklist.c` later references the symbols when `CONFIG_SYSTEM_REVOCATION_LIST` is enabled.

## State And Persistence Behavior

The embedded bytes are `__INITRODATA`, loaded during boot and available to the revocation loader. The source of persistence is the build artifact generated from configured revocation certificates.

## Dependencies And Integration Points

It depends on `linux/export.h`, `linux/init.h`, and the generated file `certs/x509_revocation_list`. It integrates with `load_revocation_certificate_list()` in `blacklist.c`.

## Risks And Edge Cases

The generated file must exist when this object is built. Size symbol width must match architecture word size. Empty revocation lists should produce a zero size and be handled gracefully by the loader.

## Test Signals

Build with empty and populated `CONFIG_SYSTEM_REVOCATION_KEYS`, verify exported size, and confirm boot logs/load behavior for compiled-in revocation certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/revocation_certificates.S -->
