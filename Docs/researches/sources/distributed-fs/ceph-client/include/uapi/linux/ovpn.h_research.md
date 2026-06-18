# sources/distributed-fs/ceph-client/include/uapi/linux/ovpn.h

Purpose: Defines the YAML-generated Generic Netlink UAPI for the in-kernel OpenVPN data channel.

Important APIs/types/functions: Exports `OVPN_FAMILY_NAME`, `OVPN_FAMILY_VERSION`, `OVPN_NONCE_TAIL_SIZE`, cipher algorithms, peer deletion reasons, key slots, nested peer attributes, key configuration attributes, key direction attributes, top-level attributes, commands, and multicast group `OVPN_MCGRP_PEERS`.

Control flow: Userspace configures peers with `OVPN_CMD_PEER_NEW/SET/GET/DEL`, receives deletion and float notifications, installs/queries/swaps/deletes keys with key commands, and passes nested peer/key attributes such as remote/local addresses, ports, sockets, keepalive settings, VPN addresses, counters, tx ID, key slot, key ID, cipher algorithm, cipher keys, and nonce tails.

State and persistence behavior: Kernel state includes peer table entries, transport socket association, VPN/link counters, keepalive timers, current and secondary key slots, cipher material, and nonce tails. The header defines netlink state exchange only; configured peers and keys are runtime state.

Dependencies and integration points: It is auto-generated from `Documentation/netlink/specs/ovpn.yaml` and integrates with YNL tooling, Generic Netlink policy, OpenVPN userspace, UDP/TCP sockets, network namespaces, and crypto implementations for AES-GCM and ChaCha20-Poly1305.

Risks: Generated UAPI must stay in sync with the YAML spec. Key attributes carry sensitive material and must be validated, zeroized in kernel paths, and not emitted unexpectedly. Socket netns IDs, peer floating, and notification ordering can cause stale peer state in userspace.

Test signals: Regenerate header from YAML and compare, use YNL tests for every command, add/get/delete peers, install/swap/delete primary and secondary keys, verify multicast notifications, test unsupported cipher rejection, and inspect counter updates under traffic.
