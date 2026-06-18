# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/sap.h

## Purpose

`sap.h` is the protocol contract for SAP, the Intel wireless host/CSME interface used by iwlmei. It documents the handshake, ownership model, host driver state messages, and data forwarding model, then defines all wire-format MEI messages, SAP notifications, data headers, ownership values, connection data, filters, NVM payloads, rfkill flags, SAR limits, and PLDR structures.

## Important APIs, Types, and Functions

The header has no functions; its public surface is packed protocol data. Core types include `struct iwl_sap_me_msg_hdr`, `struct iwl_sap_me_msg_start`, `struct iwl_sap_me_msg_start_ok`, `enum iwl_sap_msg`, `struct iwl_sap_hdr`, `struct iwl_sap_msg_dw`, `enum iwl_sap_nic_owner`, `struct iwl_sap_notif_connection_info`, host link up/down/NIC/MCC/SAR structures, `struct iwl_sap_nvm`, filter structures, `struct iwl_sap_oob_filters`, `struct iwl_sap_csme_filters`, `struct iwl_sap_cb_data`, and PLDR request/ack/end payloads.

## Control Flow

The defined flow is: MEI client startup sends `SAP_ME_MSG_START`, CSME replies `SAP_ME_MSG_START_OK`, and both sides then use MEI `CHECK_SHARED_AREA` messages as shared-memory doorbells. Host lifecycle messages advertise WiFi-driver up/down, host link state, country/SAR/NIC/radio state, ownership requests/confirmations, and host shutdown. CSME messages report AMT state, filters, connection status, NVM data, ownership requests, and PLDR acknowledgements.

## State and Persistence Behavior

All multi-byte fields intended for the wire are little-endian unless explicitly network-order IP/port fields are used. Most structures are `__packed`, so both host and CSME must preserve exact layout. The filter block can persist across many packets after `main.c` RCU-publishes it. NVM, rekey, radio, connection, and ownership fields are not stored here but are cached by `main.c` consumers.

## Dependencies and Integration Points

The header maps SAP auth/cipher enumerations to public iwlmei constants from `mei/iwl-mei.h`. It is consumed by `main.c`, `net.c`, and tracepoint headers. External integration depends on CSME firmware using the same numeric message IDs and packed layouts.

## Risks and Edge Cases

Protocol drift is the main risk: changing enum values, packing, array sizes, or endian annotations breaks firmware compatibility. Several documented fields are marked TODO/TBD, which limits validation of host-suspend and filter behavior. `struct iwl_sap_cb_data` has a flexible payload and a special DHCP filter bit, so length checks must happen in users. IPv6 and VLAN filter definitions exist even though current `net.c` support is incomplete.

## Test Signals

Compile-time checks should validate expected structure sizes where firmware ABI demands them. Runtime tests should cover SAP v3/v4 negotiation, message length validation in `main.c`, filter application in `net.c`, NVM conversion, PLDR request/ack, and ownership transfer message ordering.
