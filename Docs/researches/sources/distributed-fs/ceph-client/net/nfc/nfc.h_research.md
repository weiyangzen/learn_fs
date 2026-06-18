# sources/distributed-fs/ceph-client/net/nfc/nfc.h

## Purpose

This private NFC header declares internal types, constants, helpers, and cross-file entry points for the kernel NFC subsystem. It connects raw sockets, generic netlink, LLCP, AF_NFC protocol registration, and the core NFC device lifecycle without exposing these internals as public uapi.

## Important APIs, Types, and Functions

The header defines target mode constants `NFC_TARGET_MODE_IDLE` and `NFC_TARGET_MODE_SLEEP`, `struct nfc_protocol` for AF_NFC protocol registration, `struct nfc_rawsock` for raw/seqpacket socket state, and `struct nfc_sock_list` for protected socket lists. Accessors include `nfc_rawsock()`, `to_rawsock_sk()`, `nfc_put_device()`, and class iterator helpers.

Declarations cover LLCP MAC notifications, LLCP device registration, remote/general bytes, data receive, local lookup/refcounting, SDP TLV cleanup, raw socket init/exit, AF_NFC init/exit and protocol registration, netlink init/exit and event emitters, device lookup, firmware download, device up/down, polling, DEP link management, target activation/deactivation, data exchange, and secure element enable/disable.

## Control Flow

This header itself has no runtime control flow. Its value is in defining the callable graph among NFC compilation units. For example, `rawsock.c` uses `nfc_get_device()`, target activation, and data exchange declarations; `netlink.c` uses LLCP and core device functions; NFC device code can call the netlink event emitters declared here.

## State and Persistence

The state shape declared here includes `nfc_rawsock` fields for connected device pointer, target index, transmit work, and scheduling flag, plus socket list locking. External declarations for `nfc_devlist_generation` and `nfc_devlist_mutex` describe shared device-list state maintained elsewhere. There is no persistence beyond kernel object lifetime.

## Dependencies and Integration Points

It includes `<net/nfc/nfc.h>` and `<net/sock.h>` and is included by NFC internal C files. It is the integration seam between NFC core, LLCP, generic netlink, raw sockets, and protocol registration.

## Risks and Edge Cases

Because this header centralizes internal prototypes, mismatched lifetime assumptions can spread across files. `nfc_put_device()` is a simple `put_device()` wrapper, so callers must hold valid references. Socket-state macros rely on `struct nfc_rawsock` embedding `struct sock` as the first member.

## Test Signals

Compile coverage with NFC, LLCP, raw sockets, and netlink enabled is the main signal. Runtime tests should verify that declared lifecycle pairings are balanced: init/exit, get/put device, LLCP local get/put, and AF_NFC protocol register/unregister.
