# sources/distributed-fs/ceph-client/net/tipc/crypto.h

## Purpose

`crypto.h` declares the public TIPC crypto interface and the wire-format encryption header used by `crypto.c` and link/bearer paths. It is compiled only under `CONFIG_TIPC_CRYPTO`, so it defines the contract for encrypted TIPC packets without burdening non-crypto builds.

## Important APIs, Types, and Functions

The header defines encryption version `TIPC_EVERSION`, AES-GCM key/salt/IV/tag sizes, crypto modes `CLUSTER_KEY` and `PER_NODE_KEY`, and the exported sysctls `sysctl_tipc_max_tfms` and `sysctl_tipc_key_exchange_enabled`. The central type is packed `struct tipc_ehdr`, whose first word carries version, user, destination-known bit, TX key, peer RX-active key, keepalive, master-key, and no-RX-key indications. It also stores a 64-bit sequence number and either a node address or 128-bit node ID for LINK_CONFIG.

Public prototypes cover crypto object lifecycle, timeouts, transmit/receive, key initialization/flushing/distribution, MSG_CRYPTO receive, rekey scheduling, user-key validation, and encrypted-header validation. Inline helpers `msg_key_gen()`, `msg_set_key_gen()`, `msg_key_mode()`, and `msg_set_key_mode()` reserve bits in message word 4 for key distribution metadata.

## Control Flow

Callers use this header by creating TX/RX crypto objects with `tipc_crypto_start()`, feeding outgoing skbs through `tipc_crypto_xmit()`, validating encrypted headers with `tipc_ehdr_validate()`, and decrypting inbound skbs through `tipc_crypto_rcv()`. Key-management control flows through `tipc_crypto_key_init()`, `tipc_crypto_key_distr()`, `tipc_crypto_msg_rcv()`, and `tipc_crypto_rekeying_sched()`.

## State and Persistence Behavior

The header itself has no storage other than external sysctl declarations. It defines persistent on-wire state encoded in `struct tipc_ehdr`: key index, sequence number, peer key status, and source address or node ID. Header sizes `EHDR_SIZE`, `EHDR_CFG_SIZE`, and `EMSG_OVERHEAD` are used to size skb headroom/tailroom and link MSS calculations.

## Dependencies and Integration Points

It includes `core.h`, `node.h`, `msg.h`, and `bearer.h`, tying crypto to TIPC message layout, node identity, and media bearer abstractions. `link.c` uses `EMSG_OVERHEAD` to reduce MSS when crypto is enabled and dispatches decrypted `MSG_CRYPTO` messages. Netlink and sysctl code use validation and rekey/key APIs declared here.

## Risks and Edge Cases

The packed bitfield layout is endian-sensitive and part of the wire protocol. Any change to bit positions, header sizing, or `TIPC_EVERSION` handling affects interoperability. `EMSG_OVERHEAD` must stay aligned with the actual encryption tag and header size or link fragmentation and MTU checks become wrong.

## Test Signals

Build both little-endian and big-endian configurations if available, compile with and without `CONFIG_TIPC_CRYPTO`, verify encrypted packet sizes against `EHDR_*` constants, and exercise key distribution metadata through `MSG_CRYPTO/KEY_DISTR_MSG` packet captures.
