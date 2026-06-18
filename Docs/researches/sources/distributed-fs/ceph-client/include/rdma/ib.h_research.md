# sources/distributed-fs/ceph-client/include/rdma/ib.h

Purpose: provides generic InfiniBand address and socket-address definitions plus a safety guard for legacy RDMA file APIs that use `write()` as a bidirectional ioctl-like channel.

Important APIs and types: `struct ib_addr` is a 16-byte address union with byte/word/dword/qword accessors and aliases for raw, subnet-prefix, and interface-id fields. Inline helpers test any-address and loopback, set 32-bit words, and compare addresses. `struct sockaddr_ib` defines AF_IB socket addresses with P_Key, flow info, `ib_addr`, service ID/mask, and scope ID. `ib_safe_file_access()` returns true only when the file credential matches the current credential.

Control flow: RDMA core or userspace-facing paths manipulate IB addresses using the inline helpers. Legacy file operations should call `ib_safe_file_access()` before accepting write-triggered commands to avoid privileged writes through inherited or redirected file descriptors.

State and persistence: no state is stored. All helpers operate on caller-supplied stack/heap structures or file credentials.

Dependencies and integration points: depends on Linux credentials, current task, file structures, uaccess/fs types, and endian/network helpers. It integrates AF_IB address handling with RDMA userspace and legacy char-device/file paths.

Risks and test signals: risks include endian mistakes in address comparisons/setup, incorrect loopback detection, misuse of AF_IB fields as IP addresses, and skipping credential checks on legacy write APIs. Test address helper unit cases, AF_IB socket bind/connect paths, credential mismatch cases for inherited file descriptors, and compat/user ABI builds.
