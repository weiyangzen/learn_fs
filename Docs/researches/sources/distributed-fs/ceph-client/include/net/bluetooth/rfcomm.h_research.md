# sources/distributed-fs/ceph-client/include/net/bluetooth/rfcomm.h

## Purpose
This header defines the Linux Bluetooth RFCOMM protocol interface: wire-frame constants, multiplexer command records, core session and DLC state, socket address/options, TTY ioctl ABI, and exported RFCOMM core/socket/TTY entry points. It bridges the RFCOMM core implementation, Bluetooth sockets, and optional RFCOMM TTY devices.

## Important APIs, Types, And Constants
- Frame and MCC constants include `RFCOMM_SABM`, `DISC`, `UA`, `DM`, `UIH`, `PN`, `MSC`, `RPN`, `RLS`, `FCON`, `FCOFF`, `TEST`, and `NSC`.
- `struct rfcomm_hdr`, `rfcomm_cmd`, `rfcomm_mcc`, `rfcomm_pn`, `rfcomm_rpn`, `rfcomm_rls`, and `rfcomm_msc` model RFCOMM control frames and parameter negotiation.
- `struct rfcomm_session` holds the underlying L2CAP socket, session timer, state/flags, initiator role, default credit-flow-control state, MTU, and DLC list.
- `struct rfcomm_dlc` is the channel object with queue, timer, mutex, state/flags, refcount, DLCI/address/priority, V.24 modem status, security/deferred setup fields, MTU, credit counters, owner pointer, and callbacks for data, state, and modem-status events.
- Exported functions manage DLC allocation/free/open/close/send, modem status, accept/deferred setup, duplicate lookup, session address extraction, socket lifecycle, connection indications, TTY initialization, and RFCOMM device ioctl handling.
- `struct sockaddr_rc`, `struct rfcomm_conninfo`, `struct rfcomm_pinfo`, and `RFCOMM_LM_*` define the socket-facing ABI.
- RFCOMM TTY ioctls and records (`RFCOMMCREATEDEV`, `RFCOMMRELEASEDEV`, `RFCOMMGETDEVLIST`, `RFCOMMGETDEVINFO`, `RFCOMMSTEALDLC`) expose device creation and introspection.

## Control Flow And State
DLC users allocate a `rfcomm_dlc`, set callbacks/security policy, then call `rfcomm_dlc_open()` with source/destination addresses and channel. The core creates or finds a session, negotiates PN and security, exchanges SABM/UA, manages credit-based flow control, and moves the DLC through connection states. Transmit paths queue `sk_buff`s through `rfcomm_dlc_send()` and use `tx_credits`, `RFCOMM_TX_THROTTLED`, and MTU fragmentation. Receive paths invoke the `data_ready` callback and can call `rfcomm_dlc_throttle()` or `rfcomm_dlc_unthrottle()`, which atomically gate calls to `__rfcomm_dlc_throttle()` and `__rfcomm_dlc_unthrottle()`. Close paths send DISC or tear down immediately depending on state and error.

## State And Persistence Behavior
RFCOMM state is runtime-only in this header. Sessions and DLCs are list-linked and timer-driven. DLC lifetime is governed by `refcount_t` through `rfcomm_dlc_hold()` and `rfcomm_dlc_put()`, with final release calling `rfcomm_dlc_free()`. Synchronization is per-DLC mutex plus bit flags. TTY device data exposed through ioctl persists only while the RFCOMM module/device exists; no durable storage is defined here.

## Dependencies And Integration Points
The header depends on Bluetooth address types, socket/sk_buff/list/timer/mutex/refcount infrastructure, ioctl encoding, and optional `CONFIG_BT_RFCOMM_TTY`. Implementations are in `net/bluetooth/rfcomm/core.c`, `sock.c`, and TTY code. Socket protocol setup calls `rfcomm_init_sockets()` and cleanup calls `rfcomm_cleanup_sockets()`. TTY support compiles to no-op inline functions when disabled.

## Risks
- Incorrect refcounting or callback invocation after `rfcomm_dlc_put()` can create use-after-free bugs.
- Credit-flow-control bookkeeping can stall data if `rx_credits`/`tx_credits` and throttle bits diverge.
- RFCOMM wire structs are packed and sometimes variable-length; parsers must validate lengths before interpreting `rfcomm_hdr.len`.
- Deferred setup and security flags (`RFCOMM_SEC_PENDING`, `AUTH_PENDING`, `AUTH_ACCEPT`, `AUTH_REJECT`, `DEFER_SETUP`) are sensitive to races between socket user actions and core timers.
- TTY ioctls are userspace ABI and must retain structure sizes and visible flag meanings.

## Test Signals
- RFCOMM socket tests should cover connect, accept, deferred setup, close during negotiation, send fragmentation, credit exhaustion/replenishment, and modem-status exchange.
- TTY tests should cover create/release/list/info/steal ioctl behavior with and without `CONFIG_BT_RFCOMM_TTY`.
- Fault-injection around timers, security rejection, malformed PN/RPN/MSC frames, and concurrent close/send is valuable.
