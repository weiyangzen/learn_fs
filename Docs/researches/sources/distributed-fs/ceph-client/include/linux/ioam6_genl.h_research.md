# sources/distributed-fs/ceph-client/include/linux/ioam6_genl.h

Purpose: This header is the kernel wrapper for IPv6 IOAM Generic Netlink UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6_genl.h>` and adds no new kernel-only APIs.

Control flow: There is no runtime flow; inclusion exposes generic-netlink command, attribute, and family definitions from UAPI to kernel networking code.

State and persistence: No persistent state is defined in this wrapper.

Dependencies and integration points: Integrates IOAM control-plane definitions with generic netlink handlers and user/kernel ABI declarations.

Risks: Diverging from the UAPI header would risk ABI confusion. Kernel code should treat this as a forwarding header and keep policy/handler state elsewhere.

Test signals: Compile IOAM generic netlink code, validate UAPI attribute policy consumers, and include this header in both enabled and modular networking configurations.
