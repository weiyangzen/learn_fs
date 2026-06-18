# sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h` defines the 1-Wire netlink connector wire protocol shared by the kernel implementation and in-kernel callers. It names connector flags, top-level 1-Wire message types, command opcodes, flexible-array message layouts, and kernel-only function prototypes. The complete 135-line header was read for this report.

## Important APIs, Types, and Functions

`enum w1_cn_msg_flags` currently exposes `W1_CN_BUNDLE`, allowing a userspace request to ask for bundled replies. `enum w1_netlink_message_types` defines notifications and requests such as `W1_SLAVE_ADD`, `W1_SLAVE_REMOVE`, `W1_MASTER_ADD`, `W1_MASTER_REMOVE`, `W1_MASTER_CMD`, `W1_SLAVE_CMD`, and `W1_LIST_MASTERS`. `struct w1_netlink_msg` contains `type`, `status`, payload `len`, a union of 8-byte slave id and master id, and flexible `data[]`. `enum w1_commands` defines `W1_CMD_READ`, `W1_CMD_WRITE`, `W1_CMD_SEARCH`, `W1_CMD_ALARM_SEARCH`, `W1_CMD_TOUCH`, `W1_CMD_RESET`, `W1_CMD_SLAVE_ADD`, `W1_CMD_SLAVE_REMOVE`, and `W1_CMD_LIST_SLAVES`. `struct w1_netlink_cmd` contains a command byte, reserved byte, payload length, and flexible data. Kernel builds see prototypes for `w1_netlink_send()`, `w1_init_netlink()`, and `w1_fini_netlink()`.

## Control Flow

The header has no executable control flow. It documents the nesting used by the source implementation: `nlmsghdr`, then `cn_msg`, then one or more `w1_netlink_msg` records, each optionally containing one or more `w1_netlink_cmd` records.

## State and Persistence Behavior

No storage is owned by the header. The structures are ABI layouts for transient connector messages. The `status` and `len` fields carry per-message or per-command result state across one request/reply exchange, and master/slave identifiers connect the message to state owned by the 1-Wire core.

## Dependencies and Integration Points

The header includes `<asm/types.h>`, `<linux/connector.h>`, and `w1_internal.h`. It integrates the 1-Wire subsystem with Linux connector by using connector messages as a transport and with userspace daemons/tools that know this exact binary layout.

## Risks and Edge Cases

This file is a protocol ABI: reordering enum values, changing field sizes, or altering structure packing would break existing userspace. The protocol uses flexible arrays and 16-bit lengths, so callers must validate nested lengths before dereferencing. Comments mention typo-level documentation issues, but the functional risk is ABI drift and inconsistent status interpretation.

## Test Signals

Signals include uapi-style binary layout checks, compile coverage in kernel and non-kernel include contexts, userspace request/reply compatibility tests against older tools, and negative parser tests for unsupported flags and malformed nested command lengths.
