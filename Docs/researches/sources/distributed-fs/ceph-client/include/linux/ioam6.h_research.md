# sources/distributed-fs/ceph-client/include/linux/ioam6.h

Purpose: This header is the kernel include wrapper for IPv6 IOAM base UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6.h>` and defines no additional kernel-only structures or helpers.

Control flow: There is no runtime control flow. Inclusion makes UAPI constants and structures available to kernel code.

State and persistence: No state is declared here.

Dependencies and integration points: Integrates IPv6 In-situ Operations, Administration, and Maintenance definitions with kernel networking code while preserving the UAPI source of truth.

Risks: Any semantic change belongs in the UAPI header; adding kernel-only definitions here could create split behavior. Include guard correctness is the only local structural concern.

Test signals: Build tests should verify users include this wrapper successfully and that IOAM code compiles against the UAPI definitions.
