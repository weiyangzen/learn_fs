# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.h

## Purpose

This header defines the tiny control protocol shared by the XDP features tester and DUT programs. It standardizes command IDs, default control/data UDP/TCP ports, and the TLV header used to exchange commands, acknowledgments, capability flags, and counters.

## Important APIs, Types, and Functions

`enum test_commands` defines `CMD_STOP`, `CMD_START`, `CMD_ECHO`, `CMD_ACK`, `CMD_GET_XDP_CAP`, and `CMD_GET_STATS`. `DUT_CTRL_PORT` is `12345`; `DUT_ECHO_PORT` is `12346`. `struct tlv_hdr` contains network-order `type`, network-order `len`, and a flexible `data[]` payload.

## Control Flow

There is no executable flow in this header. `xdp_features.c` serializes each control action as a `tlv_hdr`, waits for `CMD_ACK`, and optionally copies payload bytes from `data[]`.

## State and Persistence Behavior

No storage is owned. It defines wire-format state for one control session.

## Dependencies and Integration Points

It depends on kernel integer types (`__be16`, `__u8`) and is included by both userspace control code and companion BPF/user helpers that need matching command constants.

## Risks and Test Signals

Risks include mismatched byte order, length values smaller than the header, and command additions not handled by both peers. Signals are successful `CMD_GET_XDP_CAP`, `CMD_START`, `CMD_GET_STATS`, and `CMD_STOP` exchanges.
