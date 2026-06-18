# Research: sources/distributed-fs/ceph-client/include/linux/patchkey.h

Purpose: `patchkey.h` defines the endian-sensitive `_PATCHKEY()` macro kept for soundcard/awe compatibility and includes the UAPI patchkey definition.

Important APIs/types/functions: `_PATCHKEY(id)` expands differently on big-endian and little-endian builds after including `asm/byteorder.h` and `uapi/linux/patchkey.h`. The header explicitly tells users not to include it directly and to use soundcard headers instead.

Control flow and state: there is no runtime flow or mutable state. The macro transforms an ID into the historical patch key constant at compile time according to byte order.

Dependencies and integration points: depends on architecture byte-order definitions and UAPI sound interfaces. It integrates with OSS-compatible sound headers and any legacy userspace-visible structures expecting this encoding.

Risks and test signals: risks include wrong byte-order detection, direct inclusion outside intended wrappers, and breaking userspace ABI if the macro changes. Build tests should compile on big- and little-endian targets and compare generated constants with UAPI expectations.
