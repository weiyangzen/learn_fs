# sources/distributed-fs/ceph-client/include/linux/netfilter_defs.h

Purpose: Provides small shared netfilter hook-count constants over the UAPI netfilter definitions.

Important APIs, types, and functions: Exports `NF_ARP_NUMHOOKS` and `NF_MAX_HOOKS`. Detected source surface: 12 lines; includes `uapi/linux/netfilter.h`; macros `NF_ARP_NUMHOOKS`, `NF_MAX_HOOKS`, `__LINUX_NETFILTER_CORE_H_`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no runtime flow; macros are consumed at compile time for array sizing and hook iteration bounds.

State and persistence behavior: No state is stored. The constants are compile-time ABI assumptions for hook arrays.

Dependencies and integration points: Depends on UAPI netfilter hook numbering and is included by netfilter core users.

Risks and test signals: Risks are hook-count drift if UAPI families change. Test by building all netfilter families and running hook registration selftests.
