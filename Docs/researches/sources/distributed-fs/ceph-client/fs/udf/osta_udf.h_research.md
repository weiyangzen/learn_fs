# sources/distributed-fs/ceph-client/fs/udf/osta_udf.h

## Purpose
`osta_udf.h` is the Linux copy of OSTA UDF 2.60 identifiers, suffixes, partition-map structures, allocation-descriptor implementation-use structures, and OS identifier constants. It binds Linux UDF code to the normative on-disk layout beyond base ECMA-167.

## Important APIs, types, and functions
There are no functions. Important definitions include UDF entity identifier strings such as `UDF_ID_COMPLIANT`, `UDF_ID_VIRTUAL`, `UDF_ID_SPARABLE`, and `UDF_ID_METADATA`; suffix types `domainIdentSuffix`, `UDFIdentSuffix`, `impIdentSuffix`, and `appIdentSuffix`; LVID implementation-use data; partition-map types for virtual, sparable, and metadata partitions; VAT 2.0; sparing tables; metadata-file ICB file types; and OS class/id values.

## Control flow
The header participates through structure casts and string comparisons in `super.c`, `partition.c`, `namei.c`, and inode metadata paths. Mount-time parsing uses it to classify partition maps and domain identifiers; LVID open/close writes Linux OS identifiers into `impIdent.identSuffix`.

## State and persistence
All structures are packed on-disk contracts. Incorrect changes alter media compatibility and persisted metadata interpretation. Constants identify write-protected domains, append-only VAT media, sparable media, metadata partitions, and allocation descriptor erase state.

## Dependencies and integration points
It includes `ecma_167.h` and is included through `udfdecl.h`. It is a cross-file schema contract for UDF mount, allocation, namespace, symlink, and statfs code.

## Risks and test signals
Risks are ABI/layout drift, string identifier mismatches, endian misuse by callers, and unsupported feature constants being interpreted as writable. Test signals are mounting media with UDF 1.50 virtual maps, sparable maps, UDF 2.50 metadata partitions, write-protected domain flags, and LVID implementation-use records created by Linux and non-Linux systems.
