# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_metadata.h

## Purpose

This header defines shared protocol constants and the metadata block used by XDP metadata selftests. The companion BPF program writes `struct xdp_meta` before packet data, and userspace reads it to validate hardware RX hints.

## Important APIs, Types, and Functions

The header provides fallback Ethernet protocol constants for IPv4, IPv6, 802.1Q, and 802.1AD, a fallback `BIT()` macro, `XDP_CHECKSUM_MAGIC`, `enum xdp_meta_field`, and `struct xdp_meta`. The metadata struct carries timestamp or timestamp error, XDP timestamp, RX hash, hash type or error, VLAN proto/TCI or error, and a `hint_valid` bitmask.

## Control Flow

No code runs here. Producers set fields and `hint_valid` bits; consumers branch on `XDP_META_FIELD_TS`, `XDP_META_FIELD_RSS`, and `XDP_META_FIELD_VLAN_TAG` to interpret union members as either values or errors.

## State and Persistence Behavior

The layout is transient per packet and stored adjacent to XDP packet data, usually in AF_XDP UMEM. It has no file-backed persistence.

## Dependencies and Integration Points

It integrates BPF-side metadata extraction with userspace validation in `xdp_hw_metadata.c`. It depends on Linux fixed-width integer types and common Ethernet protocol IDs.

## Risks and Test Signals

Risks are ABI drift between BPF and userspace, incorrect union interpretation when `hint_valid` is wrong, and endianness mistakes in VLAN protocol fields. Signals are userspace printing correct metadata values or explicit error codes per field.
