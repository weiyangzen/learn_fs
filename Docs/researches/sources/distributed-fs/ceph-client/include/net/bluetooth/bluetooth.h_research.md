# sources/distributed-fs/ceph-client/include/net/bluetooth/bluetooth.h

## Purpose

`bluetooth.h` is the common in-kernel Bluetooth header for protocol numbers, socket options, address types, logging helpers, common socket state, skb control blocks, skb allocation/send helpers, and subsystem initialization entry points.

## Important APIs, Types, and Functions

The header defines AF/PF Bluetooth values, Bluetooth protocol numbers (`BTPROTO_L2CAP`, `BTPROTO_HCI`, `BTPROTO_SCO`, `BTPROTO_ISO`, and others), socket options for security, deferred setup, flushable traffic, power, channel policy, voice, MTU, PHY, mode, packet status, ISO QoS, codec selection, ISO BASE, and packet sequence numbers. It defines ISO QoS structures for unicast and broadcast, codec capability layouts, `enum bt_sock_state`, `bdaddr_t`, address type helpers, and address copy/compare/swap helpers.

`struct bt_sock` embeds `struct sock` and adds accept queue, parent pointer, flags, and skb metadata callbacks. `struct bt_skb_cb` overlays `skb->cb` with packet type, activity/status/sequence metadata, and protocol-specific L2CAP/HCI/MGMT/control data. Helpers allocate Bluetooth skbs with `BT_SKB_RESERVE`, copy sendmsg payloads into one skb or a fragment list, convert Bluetooth status/errno values, manage HCI socket flags, initialize Bluetooth sockets/sysfs/procfs/debugfs, and initialize or stub L2CAP/SCO/ISO/MGMT subsystems depending on configuration.

## Control Flow

Bluetooth protocol modules register socket families with `bt_sock_register()`, allocate sockets through `bt_sock_alloc()`, and share recvmsg/poll/ioctl/wait helpers. Send paths use `bt_skb_sendmsg()` or `bt_skb_sendmmsg()` to reserve protocol headroom, enforce MTU chunking, copy from the userspace iterator, and attach socket priority. Accepting protocols use `bt_accept_enqueue()`, `bt_accept_unlink()`, and `bt_accept_dequeue()`. Subsystem init functions bring up HCI socket, L2CAP, SCO, ISO, MGMT, sysfs, and procfs pieces.

## State and Persistence Behavior

There is no durable storage. Runtime state lives in Bluetooth sockets, skb control blocks, accept queues, proc/debugfs/sysfs registrations, and protocol subsystem globals. Address and QoS structures are ABI data passed between kernel and userspace.

## Dependencies and Integration Points

The header depends on Linux sockets, sk_buffs, poll, seq_file, ethtool timestamp reporting, optional debug support, and Bluetooth HCI/L2CAP/SCO/ISO/MGMT modules. It is included widely by Bluetooth core, socket protocols, monitor/control code, and drivers.

## Risks and Edge Cases

`bt_skb_sendmmsg()` can return the first skb even if later fragment allocation fails, leaving partial data semantics to callers. `bt_skb_cb` shares limited skb control space; all protocols must respect the overlay. Address type validation distinguishes only BR/EDR, LE public, and LE random. Flexible-array ABI structs need strict length validation in socket option handlers. Conditional SCO/ISO stubs must free skbs and return clear errors when features are disabled.

## Test Signals

Test socket option ABI sizes, address type validation, sendmsg and multi-fragment send paths, shutdown/error handling in `bt_skb_send_alloc()`, accept queue operations, skb control block preservation through HCI/L2CAP paths, debug logging enablement, subsystem init/cleanup under `CONFIG_BT_BREDR` and `CONFIG_BT_LE`, and proc/sysfs/debugfs registration.
