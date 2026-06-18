## sources/distributed-fs/ceph-client/include/uapi/linux/dns_resolver.h

Purpose: This header defines the binary payload layout for the kernel DNS resolver key type, especially server-list payloads requested with `srv=1`. It gives userspace resolvers and kernel clients a compact typed format for DNS-derived service records.

Important APIs and types: Enums describe content type, address type, server transport protocol, record source, and lookup status. `struct dns_payload_header` marks a binary payload with a leading zero, content type, and version. `struct dns_server_list_v1_header` adds source, status, and server count. `struct dns_server_list_v1_server` stores name length, SRV priority/weight/port, source/status/protocol, and address count. `struct dns_server_list_v1_address` prefixes variable address bytes as IPv4 or IPv6.

Control flow and state: A resolver produces a payload beginning with a binary header, followed by a v1 server-list header, then repeated server records. Each server record is immediately followed by a non-NUL-terminated name and then address records. Kernel clients parse counts and lengths to locate variable records.

Persistence and dependencies: Payloads are stored in kernel keyring DNS resolver keys and expire according to key/resolver policy outside this header. The ABI depends only on `<linux/types.h>` and uses packed structs, so byte layout is part of the contract.

Integration points: It is relevant to kernel subsystems that perform upcalls for DNS names, including distributed filesystems and network filesystems that need service discovery. Userspace helpers such as keyutils resolvers must encode exactly this format.

Risks and test signals: Risks include malformed length/count fields, endian assumptions for little-endian annotated fields in comments, non-NUL names, unsupported future versions, empty records with failure status, and distinguishing local config/NSS/DNS/SRV sources. Tests should parse mixed IPv4/IPv6 records, bad lengths, zero-server failures, partial decoding statuses, unsupported content or version values, and resolver cache refresh behavior.
