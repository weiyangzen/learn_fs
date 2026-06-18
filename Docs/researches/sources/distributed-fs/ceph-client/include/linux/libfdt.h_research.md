# sources/distributed-fs/ceph-client/include/linux/libfdt.h

Purpose: kernel wrapper that adapts the device-tree compiler's libfdt header for Linux kernel users.

Important APIs and types: this file includes `linux/libfdt_env.h` and then the shared `scripts/dtc/libfdt/libfdt.h`, exposing libfdt parsing and mutation APIs under the kernel environment definitions.

Control flow: kernel code includes this wrapper when it needs flattened device tree access; control flow is implemented in the upstream libfdt functions.

State and persistence: no state is owned here. Libfdt operates on caller-provided FDT blobs.

Dependencies and integration points: depends on Linux's libfdt environment typedefs and byte-order helpers; integrates generated/embedded FDT blob handling with shared DTC libfdt code.

Risks and test signals: risks are include-path drift and environment type mismatches. Test by building FDT users and running boot-time FDT parsing/overlay paths.
