# sources/distributed-fs/ceph-client/include/uapi/linux/pfkeyv2.h

Purpose: Defines the PF_KEY v2 socket ABI for IPsec Security Association and Security Policy management, following RFC 2367 plus Linux extensions.

Important APIs/types/functions: Exports `PF_KEY_V2`, `PFKEYV2_REVISION`, packed SADB message/extension structs, SA/lifetime/address/key/identity/sensitivity/proposal/supported/algorithm/SPIRANGE structures, Linux extension structs for SA2, policy, IPsec request, NAT-T, security context, KM address, and dump filter. Defines message types, SA flags/states/types, auth/encryption/compression algorithms, extension IDs, and identity types.

Control flow: Key management daemons communicate over PF_KEY sockets by sending `sadb_msg` headers followed by 64-bit-length extension blocks. The kernel creates, updates, deletes, dumps, expires, acquires, and migrates IPsec SAs and policies based on these messages, and emits notifications back to registered daemons.

State and persistence behavior: Runtime state lives in the kernel XFRM/IPsec SAD and SPD. The ABI represents SA SPI, replay, algorithm, keys, lifetimes, addresses, identities, policies, NAT-T ports, security contexts, and migration data. SAs/policies persist until deleted, expired, flushed, or namespace teardown.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with racoon, setkey, strongSwan compatibility paths, XFRM state/policy management, SELinux/LSM contexts, NAT traversal, and network namespaces.

Risks: Packed layouts and RFC-specified length units must be exact. Key material is sensitive and must be copied, validated, and zeroed carefully. Algorithm IDs include legacy and Linux-specific values; arbitrary renumbering would break key daemons. Extension parsing must reject malformed lengths.

Test signals: Run PF_KEY key-manager tests, add/update/delete AH/ESP/IPComp SAs, install SPD entries, dump/filter SAs, test NAT-T and security contexts, validate expire/acquire notifications, fuzz extension length/order, and compare behavior with XFRM netlink equivalents.
