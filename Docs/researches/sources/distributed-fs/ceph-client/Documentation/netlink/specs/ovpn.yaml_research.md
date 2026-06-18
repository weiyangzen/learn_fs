# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovpn.yaml

Purpose: specifies the Generic Netlink API for controlling OpenVPN network devices in the kernel, including peers, session keys, key rotation, deletion, and peer endpoint floating notifications.

Important APIs/types/functions: definitions include `nonce-tail-size`, `cipher-alg`, `del-peer-reason`, and `key-slot`. Attribute sets model peer state (`peer`), peer input subsets for new/set/delete, key configuration (`keyconf`, `keydir`, `keyconf-get`, swap/delete inputs), top-level `ovpn`, and operation-specific wrappers that include `ifindex`. Peer fields cover ids, remote/local/VPN IPv4 and IPv6 addresses, scope id, ports, socket and netns id, keepalive settings, deletion reason, traffic counters, and transmit id. Key fields include peer id, slot, key id, cipher algorithm, encrypt/decrypt dirs, cipher key, and nonce tail.

Control flow: peer operations are `peer-new`, `peer-set`, `peer-get`, and `peer-del`, with peer delete and peer float notifications reusing `peer-get`. Key operations are `key-new`, `key-get`, `key-swap`, and `key-del`, plus a key-swap notification when IV space exhaustion requires renegotiation. Most operations name `ovpn-nl-pre-doit` and `ovpn-nl-post-doit`, implying device lookup/reference management around each request. Administrative permission is required throughout.

State and persistence: represented state is live OpenVPN device peer tables, socket associations, endpoint addresses, counters, keepalive parameters, and primary/secondary key material. Keys are sensitive runtime state; `key-get` intentionally returns non-sensitive key/cipher metadata rather than raw key material.

Dependencies and integration points: integrates kernel OpenVPN data path, net_device ifindex lookup, socket ownership, network namespaces, cipher/key management, and userspace OpenVPN control daemons.

Risks: key and nonce fields are security-sensitive, so length validation and zeroization are important outside the YAML. Peer ids and tx ids are bounded to 24 bits, and key ids to 3 bits; tools must enforce these limits. IPv6 scope, socket-netnsid, endpoint floating, and socket fd/id semantics cross namespace boundaries. Notifications are important for renegotiation; missing them can break key rollover.

Test signals: peer create/set/get/delete round trips, key create/get/swap/delete flows without leaking key bytes, nonce-tail exact length, id bound enforcement, endpoint float notifications, key exhaustion notification handling, and namespace/socket validation.
