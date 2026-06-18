# sources/distributed-fs/ceph-client/include/linux/ioam6_iptunnel.h

Purpose: This header is the kernel wrapper for IPv6 IOAM lightweight tunnel UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6_iptunnel.h>` and declares no additional local types.

Control flow: No runtime behavior is implemented. The header exposes tunnel-related IOAM UAPI constants and structures.

State and persistence: No state is owned here; tunnel state lives in networking/lwtunnel implementation code.

Dependencies and integration points: Provides the kernel include path for IOAM lwtunnel code and users of the corresponding netlink tunnel attributes.

Risks: Local edits could desynchronize kernel declarations from userspace ABI. This file should remain a thin wrapper unless a kernel-only helper is strongly justified.

Test signals: Compile IOAM lightweight tunnel support, netlink attribute parsing, and disabled-feature builds that still include the wrapper.
