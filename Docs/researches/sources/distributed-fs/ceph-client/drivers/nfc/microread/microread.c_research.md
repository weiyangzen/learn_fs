# sources/distributed-fs/ceph-client/drivers/nfc/microread/microread.c

Purpose: Implements the Inside Secure Microread chipset HCI logic independent of physical transport. It defines proprietary gates/pipes/events, registers an NFC HCI device, configures polling subscriptions, translates target discovery and DEP events, handles initiator/target data exchange, and exports probe/remove for I2C and MEI transports.

Important APIs, types, and functions: `struct microread_info` stores transport callbacks and pending async transceive callback. `microread_hci_ops` wires open/close, `hci_ready`, `start_poll`, DEP link up/down, target mapping, initiator transceive, target send, and event receive callbacks. `microread_probe()` allocates/registers the HCI device with gate table and supported protocols; `microread_event_received()` dispatches chipset events; `microread_target_discovered()` converts card-found payloads into `struct nfc_target`.

Control flow: Open enables the PHY. HCI ready subscribes reader gates to card discovery. Polling stops old discovery, sets P2P target mode, configures general bytes for NFC-DEP initiator/target, then starts selected discovery. Initiator transceive either sends P2P exchange events or proprietary reader exchange commands with control bits and optional Type 1 CRC. Async completion strips RF status and invokes the NFC callback. Event receive handles card discovery, P2P activation/deactivation, and target-mode data exchange.

State and persistence behavior: Runtime state includes transport ID/ops, HCI device, async callback type/function/context, HCI gate/pipe table, session id, and HCI core state. No persistent storage is used.

Dependencies and integration points: Uses NFC HCI core, NFC target/DEP APIs, LLC names supplied by transports, CRC-CCITT for Jewel/Type 1 commands, SKBs, and transport `nfc_phy_ops`.

Risks: Many event payload parsers assume minimum lengths before indexing fixed offsets. Async callback state is single outstanding operation state and would not support concurrent transceives. Gate-specific control bits and UID offsets are chipset protocol details; mistakes cause silent RF failures. General bytes allocation can disable NFC-DEP polling if unavailable.

Test signals: HCI registration/removal, I2C and MEI transports, polling protocol masks, ISO A/B/Felica/Jewel target discovery payloads, malformed short payloads, Type 1 CRC transceive, NFC-DEP link up/down and target mode exchange, async error propagation, and event fallthrough to standard HCI handling.
