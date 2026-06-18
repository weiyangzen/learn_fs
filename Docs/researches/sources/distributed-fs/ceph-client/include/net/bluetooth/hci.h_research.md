# sources/distributed-fs/ceph-client/include/net/bluetooth/hci.h

## Purpose

`hci.h` is the primary Bluetooth Host Controller Interface wire-format and constants header. It describes controller/device events, bus types, quirks, device/socket/controller flags, timeouts, packet types, command opcodes and parameters, event payloads, packet headers, handle packing helpers, and LE/ISO/channel-sounding structures.

## Important APIs, Types, and Functions

The file defines maximum HCI frame sizes, link key size, HCI device and notify events, bus identifiers, a large quirk enum used by drivers before or during registration, device/socket/controller flag enums, standard timeouts, HCI packet types, ACL/SCO/eSCO/ISO packet flags, link types, LMP and LE feature bits, link policy/mode/security constants, EIR/advertising data types, HCI error codes, and invalid sentinel values.

Command definitions include BR/EDR inquiry/connection/authentication, local host/controller setup, buffer/codec queries, LE advertising/scanning/connection/privacy/data-length/PHY commands, extended advertising and periodic advertising, PAST, ISO CIG/CIS/BIG/BIS setup, ISO data path setup, LE host features, LE all-feature pages, and LE Channel Sounding commands. Event structures cover command complete/status, connection, disconnection, authentication/encryption, inquiry, remote feature/name/version, LE meta events, extended advertising reports, periodic advertising, CIS/BIG events, channel sounding events, vendor events, and stack-internal events. Inline helpers return packet headers from skbs, pack/unpack opcodes and handles, pack/unpack ISO flags and data lengths, and encode 24-bit little-endian values.

## Control Flow

HCI core and drivers build command skbs using the opcode and command-parameter structs, submit them to the controller, and parse events using the matching event structs. Event handling updates `hci_dev` and `hci_conn` state declared in `hci_core.h`, feeds upper protocols, completes synchronous requests, and notifies monitor/control sockets. The quirk and feature constants gate which commands are sent during setup, scan, advertising, connection, security, and ISO flows.

## State and Persistence Behavior

This header declares no storage. The constants and packed structs define runtime state exchanged over the HCI transport. Feature bits, quirks, command masks, and event payloads become persistent only as fields in `struct hci_dev` or `struct hci_conn` in other files; controller settings may persist in hardware depending on the command and device firmware.

## Dependencies and Integration Points

It depends on Bluetooth address types from `bluetooth.h` and Linux integer/endian annotations. It is consumed by HCI core, management, sockets, monitor, drivers, SCO/L2CAP/ISO, and users of raw HCI packets. It must match the Bluetooth Core Specification ABI exactly.

## Risks and Edge Cases

Packed structs with flexible arrays require exact skb length validation before access. Some event structs contain zero-length arrays for variable channel-sounding reports; parser code must compute offsets manually and defensively. Quirk flags are behavior-changing and often must be set before `hci_register_dev()`. Feature/command mask helpers elsewhere assume bytes and bit positions from this header are correct. Endian conversion is explicit through `__le*`; direct host-order use would corrupt wire data.

## Test Signals

Test command serialization sizes and endianness, event parser bounds for every flexible-array payload, opcode and handle pack/unpack round trips, LE extended advertising and periodic advertising report parsing, ISO data flag/length decoding, Channel Sounding variable reports, quirk-gated setup command selection, raw HCI socket monitor output, and interoperability against known controller traces.
