# sources/distributed-fs/ceph-client/net/nfc/hci/hci.h

Purpose: Defines local NFC HCI/HCP structures, constants, and internal function prototypes shared by HCI command, core, and HCP implementation files.

Important APIs and types: Key structures are `gate_pipe_map`, packed `hcp_message` and `hcp_packet`, `hcp_exec_waiter`, queued `hci_msg`, and packed admin pipe command/notification payloads. It exposes `nfc_hci_hcp_message_tx` and `nfc_hci_hcp_message_rx` to bridge command helpers and core dispatch.

Control flow: The header establishes HCP packet interpretation: packet header carries continuation/final state plus pipe; message header carries type and instruction. `HCP_HEADER`, `HCP_MSG_GET_TYPE`, and `HCP_MSG_GET_CMD` are used by transmit construction and receive dispatch.

State and persistence: No runtime state is stored here, but the declared data structures define how HCI messages persist while queued, fragmented, waiting for responses, and carrying callbacks.

Dependencies and integration points: Includes `<net/nfc/hci.h>` for public HCI constants and device definitions. Its constants must stay compatible with ETSI HCI framing and the HCI core's pipe table semantics.

Risks: Packed wire structs are cast over skb data, so callers must validate skb length before dereferencing. `NFC_HCI_FRAGMENT` is used with bit masking in both tx and rx paths; regressions here can break reassembly.

Test signals: Compile-time and unit-style skb tests should verify header packing/unpacking, packed struct sizes, and response/command/event type extraction for all HCP types.
