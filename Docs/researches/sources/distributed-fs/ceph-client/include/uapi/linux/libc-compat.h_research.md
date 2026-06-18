# sources/distributed-fs/ceph-client/include/uapi/linux/libc-compat.h

Purpose: coordinates Linux UAPI headers with C library headers so duplicate structs, enums, and macros are defined by exactly one side when headers are included in either order.

Important APIs and types: it exports guard macros such as `__UAPI_DEF_IF_IFCONF`, `__UAPI_DEF_IF_IFMAP`, `__UAPI_DEF_IF_IFNAMSIZ`, `__UAPI_DEF_IF_IFREQ`, `__UAPI_DEF_IF_NET_DEVICE_FLAGS`, `__UAPI_DEF_IN_ADDR`, `__UAPI_DEF_IN_IPPROTO`, `__UAPI_DEF_IN_PKTINFO`, `__UAPI_DEF_IP_MREQ`, `__UAPI_DEF_SOCKADDR_IN`, `__UAPI_DEF_IN_CLASS`, IPv6 equivalents, and `__UAPI_DEF_XATTR`.

Control flow: UAPI headers include this file early, then wrap conflicting definitions in `#if __UAPI_DEF_*`. If glibc headers such as `net/if.h`, `netinet/in.h`, or `sys/xattr.h` are already included, corresponding Linux definitions are suppressed. If Linux headers are included first, the macros tell libc headers to avoid redefining the same constructs. Non-glibc libraries can predefine macros to opt out.

State and persistence: no runtime state. The state is preprocessor inclusion order and feature macro detection.

Dependencies and integration points: integrates Linux UAPI headers with glibc and other libc implementations, especially networking and xattr headers. It indirectly protects downstream builds that mix libc and kernel UAPI includes.

Risks and test signals: risks are redefinition warnings/errors, missing definitions, incorrect glibc feature-test macro handling, and stale coordination as libc adds symbols. Test include-order matrices for `<linux/if.h>`, `<net/if.h>`, `<linux/in.h>`, `<netinet/in.h>`, `<linux/xattr.h>`, and `<sys/xattr.h>` under glibc and non-glibc toolchains.
