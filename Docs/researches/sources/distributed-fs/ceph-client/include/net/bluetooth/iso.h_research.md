# sources/distributed-fs/ceph-client/include/net/bluetooth/iso.h

## Purpose

`iso.h` defines Bluetooth ISO socket defaults and address structures for connected isochronous and broadcast isochronous sockets.

## Important APIs, Types, and Functions

`ISO_DEFAULT_MTU` is 251 and `ISO_MAX_NUM_BIS` is 31. `struct sockaddr_iso_bc` holds broadcast address, address type, advertising SID, number of BIS indexes, and the BIS list. `struct sockaddr_iso` contains socket family, peer address, address type, and an optional flexible broadcast address extension.

## Control Flow

ISO socket code receives these sockaddr structures during bind/connect/listen-style operations, validates address type and broadcast fields, and maps them to HCI ISO/CIS/BIS connection setup through HCI core.

## State and Persistence Behavior

No state is stored here. Address structures are transient ABI inputs/outputs for sockets.

## Dependencies and Integration Points

The header depends on Bluetooth address definitions and integrates with ISO socket code, HCI ISO connection management, CIS/BIS setup, and broadcast synchronization.

## Risks and Edge Cases

The flexible `iso_bc` extension requires careful sockaddr length validation. `bc_num_bis` must not exceed `ISO_MAX_NUM_BIS`. Broadcast and unicast address semantics differ and must not be conflated. Default MTU must stay aligned with HCI ISO payload limits.

## Test Signals

Test unicast and broadcast sockaddr lengths, maximum and zero BIS counts, invalid address types, SID handling, default MTU use, and mapping to HCI CIS/BIS connection helpers.
