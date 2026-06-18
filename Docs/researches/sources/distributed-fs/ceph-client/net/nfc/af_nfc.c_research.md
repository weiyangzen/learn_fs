# sources/distributed-fs/ceph-client/net/nfc/af_nfc.c

## Purpose

`af_nfc.c` registers the `PF_NFC` socket family and dispatches NFC socket creation to protocol-specific implementations such as raw sockets and LLCP.

## Important APIs, Types, and Functions

The file maintains `proto_tab[NFC_SOCKPROTO_MAX]` protected by `proto_tab_lock`. `nfc_sock_create()` is the family create callback. `nfc_proto_register()` and `nfc_proto_unregister()` are exported protocol registration APIs. `af_nfc_init()` registers the socket family, and `af_nfc_exit()` unregisters it.

## Control Flow

Core NFC initialization calls `af_nfc_init()`, which registers `nfc_sock_family_ops`. When userspace creates a `PF_NFC` socket, `nfc_sock_create()` rejects non-init network namespaces, validates the protocol number, takes a read lock, tries to pin the registered protocol module, and calls that protocol's create callback. Protocol modules register by first registering their `struct proto`, then inserting the protocol descriptor into `proto_tab` under the write lock.

## State and Persistence Behavior

The protocol table persists for the life of the NFC core module. Entries are added by protocols at initialization and cleared at exit. Module references are held only around create callback invocation.

## Dependencies and Integration Points

This file integrates with Linux socket family registration, `struct nfc_protocol` from NFC internals, and protocol implementations built into `nfc.o` such as raw sockets and LLCP sockets.

## Risks and Edge Cases

Only `init_net` is supported; namespace support changes would need broader NFC core review. Registration must unwind `proto_register()` on table conflicts. A protocol ID outside the table is `-EINVAL`, while an unregistered valid protocol is `-EPROTONOSUPPORT`.

## Test Signals

Create raw and LLCP NFC sockets with registered protocols, try invalid protocol IDs, verify behavior in non-init network namespaces, and exercise module unload after sockets are created and closed.
