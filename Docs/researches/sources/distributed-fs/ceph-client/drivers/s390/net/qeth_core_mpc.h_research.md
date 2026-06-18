# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_mpc.h

## Purpose

`qeth_core_mpc.h` defines the qeth MPC and IPA protocol contract. It provides command codes, return codes, feature bits, packed request/reply structures, protocol constants, byte-offset macros into MPC frames, and declarations for the immutable command templates implemented in `qeth_core_mpc.c`. It is the wire-format authority used by the qeth core and layer-specific modules.

## Important APIs, types, and constants

- Template declarations and sizes: `IPA_PDU_HEADER`, `CM_ENABLE`, `CM_SETUP`, `ULP_ENABLE`, `ULP_SETUP`, `DM_ACT`, `IDX_ACTIVATE_READ`, `IDX_ACTIVATE_WRITE`, and their `*_SIZE` constants.
- Offset macros: `QETH_IPA_PDU_LEN_*`, `QETH_IPA_CMD_DEST_ADDR`, `QETH_*_TOKEN`, `QETH_*_RESP_*`, `QETH_TRANSPORT_HEADER_SEQ_NO`, `QETH_PDU_HEADER_SEQ_NO`, and IDX activation accessors are used to patch or parse raw MPC buffers.
- Capability representation: `struct qeth_ipa_caps` and helpers `qeth_ipa_caps_supported()`, `qeth_ipa_caps_enabled()`, `qeth_adp_supported()`, `qeth_is_supported()`, `qeth_is_supported6()`, and `qeth_is_ipafunc_supported()`.
- Hardware/device enums: `enum qeth_card_types`, link types, routing types, IPA commands, IPA return codes, IPA assist flags, adapter-parameter commands, MAC/address ops, isolation modes, card-info values, diagnostic-assist commands, VNICC flags/commands, bridgeport commands, and address-change event codes.
- Packed IPA structures: SET/DEL IP and multicast payloads, L2 MAC/VLAN commands, SETASSPARMS, SETADAPTERPARMS, SNMP, QUERY OAT, QUERY CARD INFO, QUERY SWITCH ATTRIBUTES, diagnostic assist, VNICC, SETBRIDGEPORT, address-change notification, local-address notifications, and top-level `struct qeth_ipa_cmd`.
- Parser helpers: `IS_IPA_REPLY`, `PDU_ENCAPSULATION(buffer)`, and `IS_IPA(buffer)`.
- Diagnostic APIs: `qeth_get_ipa_msg()` and `qeth_get_ipa_cmd_name()` are declared here and implemented in `qeth_core_mpc.c`.

## Control flow and integration

The header is consumed in two directions. For outbound commands, `qeth_core_main.c` allocates a command buffer, copies a template, uses offset macros to patch tokens/lengths/protocol information, then overlays `struct qeth_ipa_cmd` payloads for IPA commands. For inbound data, the read callback uses `IS_IPA()` and `PDU_ENCAPSULATION()` to locate the IPA command inside a raw MPC buffer, then interprets the packed union according to `hdr.command` and `hdr.prot_version`.

Layer-specific qeth code also relies on these definitions for IP/MAC/VLAN/routing operations, offload negotiation, bridgeport/VNICC management, and event handling. The `SETASS_DATA_SIZEOF`, `SETADP_DATA_SIZEOF`, `VNICC_DATA_SIZEOF`, `SBP_DATA_SIZEOF`, and `IPA_DATA_SIZEOF` macros help callers size IPA payloads without open-coding union offsets.

## State and persistence behavior

The file defines protocol data shapes, not live state. Mutable capability and feature state is stored by callers in `struct qeth_card_options` and `struct qeth_card_info`; command instances live in transient `qeth_cmd_buffer` allocations. There is no persistence outside the active kernel driver instance and hardware state negotiated through IPA commands.

## Dependencies and integration points

This header depends on s390 qeth UAPI types from `asm/qeth.h`, Ethernet constants from `uapi/linux/if_ether.h`, IPv6 address structures, and compiler packing/offset helpers. It must remain consistent with the actual IBM OSA/IQD MPC and IPA hardware protocol, `qeth_core_mpc.c` templates, and all call sites that cast raw bytes to these packed structures.

## Risks and edge cases

- Most structures are `packed` wire layouts. Reordering fields, changing types, or removing packing can silently break hardware protocol compatibility.
- Offset macros perform byte arithmetic on raw buffers. They assume the template layout and response encapsulation remain fixed.
- `PDU_ENCAPSULATION()` and `IS_IPA()` use raw offsets from a buffer; callers must only use them with sufficiently sized MPC frames.
- Numeric return codes are reused across command families; interpretation requires both command and return code.
- Feature flags distinguish IPv4, IPv6, adapter, VNICC, and bridgeport capabilities. Mixing supported and enabled masks can lead to advertising unavailable netdev features.
- Conditional `IS_OSX()` depends on `CONFIG_QETH_OSX`, so code must compile and behave correctly when OSX support is disabled.

## Test signals

Tests should cover compile-time structure sizes/offsets where possible, successful construction of IPA SETASSPARMS/SETADAPTERPARMS/DIAG/VNICC/SBP payloads, parsing of IPA replies and unsolicited events, fallback behavior for unknown command names and return-code messages, feature negotiation for IPv4/IPv6 assists, bridgeport and VNICC command sizing, and configurations with `CONFIG_QETH_OSX` both enabled and disabled.
