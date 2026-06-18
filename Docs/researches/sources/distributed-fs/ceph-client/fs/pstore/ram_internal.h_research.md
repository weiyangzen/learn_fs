# sources/distributed-fs/ceph-client/fs/pstore/ram_internal.h

## Purpose
`ram_internal.h` defines the private `ramoops` persistent RAM zone structure, flags, and function prototypes shared by `ram.c` and `ram_core.c`.

## Important APIs, types, and functions
It defines `PRZ_FLAG_NO_LOCK`, `PRZ_FLAG_ZAP_OLD`, `struct persistent_ram_zone`, and prototypes for PRZ allocation, freeing, zapping, writing, old-log handling, and ECC notice formatting.

## Control flow
The flags guide runtime behavior: some zones use locking for updates, ftrace-style zones can skip locking for speed, and single-boot lifetime zones are zapped after their old contents are copied.

## State and persistence
The structure bridges persistent memory metadata and runtime-only helpers: physical address, mapping, buffer header, ECC layout, old-log copy, and type/label.

## Dependencies and integration points
It depends on `linux/pstore_ram.h`, Reed-Solomon types through included structures, and the pstore type enum.

## Risks and test signals
Risks include caller disagreement about flags, stale old-log pointers, ECC configuration mismatch, and no-lock writes on zones with multiple writers. Test signals are compile coverage for `ram.c`/`ram_core.c`, PRZ lifecycle tests, ftrace no-lock operation, and zap-old behavior.
