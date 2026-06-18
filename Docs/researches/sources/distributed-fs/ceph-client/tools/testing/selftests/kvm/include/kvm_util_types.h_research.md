# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util_types.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util_types.h

Purpose: shared scalar type aliases for KVM selftest guest and host addresses. It avoids repeating Linux/uapi integer choices across utility headers.

Important APIs/types/functions: the header defines address-sized aliases such as `gpa_t`, `gva_t`, `hva_t`, and related guest frame/page-number types used throughout `kvm_util.h` and architecture helpers.

Control flow and state: no control flow; it is a type contract. State behavior is indirect: these aliases determine how VM memory metadata, page-table helpers, and ucall pointers are represented.

Dependencies and integration: included by `kvm_util.h` and architecture code. It must match KVM selftest assumptions about 64-bit guest physical and virtual addresses even when host userspace types vary.

Risks: changing alias widths or signedness would affect address arithmetic, sparsebit indexes, ioctl payloads, and pointer conversions. Tests that cast between guest virtual addresses and host pointers rely on explicit use of these types.

Test signals: compile-time warnings/errors in memory helpers and runtime failures in address translation or ucall decoding are the relevant signals.
