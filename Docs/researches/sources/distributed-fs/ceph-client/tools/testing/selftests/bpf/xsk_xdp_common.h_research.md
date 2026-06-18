# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_xdp_common.h

## Purpose

This shared header provides tiny constants and a counter layout used by AF_XDP/XDP selftest programs.

## Important APIs, Types, and Functions

It defines `MAX_SOCKETS` as `2`, `PKT_HDR_ALIGN` as Ethernet header size plus two bytes for packet data alignment, and `struct xdp_info` with an aligned 64-bit `count` field.

## Control Flow

There is no executable flow. Producers and consumers use the constants to size arrays and align packet headers; BPF/user code can share `struct xdp_info` for counters.

## State and Persistence Behavior

`struct xdp_info` instances are transient counter values, typically in BPF maps or shared test state. The header itself owns no storage.

## Dependencies and Integration Points

It depends on `struct ethhdr` being visible where `PKT_HDR_ALIGN` is evaluated. It integrates `xskxceiver.c`, AF_XDP helper code, and companion XDP skeleton programs.

## Risks and Test Signals

Risks are include-order issues for `struct ethhdr`, alignment assumptions changing with packet layout, and counter false-sharing if alignment is altered. Signals are successful build and consistent packet/counter validation in XSK tests.
