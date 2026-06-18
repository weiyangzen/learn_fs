# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ifh.h

Purpose: documents the LAN966x Injection/Extraction Frame Header bit layout and field widths used by CPU injection, extraction, FDMA, PTP, QoS, forwarding, and rewriter paths.

Important APIs and types: this header defines `IFH_LEN`, `IFH_LEN_BYTES`, every `IFH_POS_*` bit position, and every `IFH_WID_*` field width. Fields include timestamp, bypass, masquerade, length, rewriter command, PDU type, source port, TCI, QoS class, CPU queue mask, destination port mask, internal priority, and many hardware classification/status fields.

Control flow and integration: no executable control flow. `lan966x_main.c` uses these positions to set IFH fields for manual injection and parse source port/length/timestamp on extraction. FDMA and PTP paths rely on the same layout for RX/TX timestamp metadata.

State and persistence: no runtime state. The constants are an ABI between software and LAN966x hardware; changing them changes packet injection/extraction semantics.

Dependencies and integration points: included by `lan966x_main.h` and therefore visible to most LAN966x modules. It must match the hardware IFH transmitted most-significant byte first.

Risks and test signals: an incorrect bit position or width silently misroutes packets, breaks PTP timestamp IDs, corrupts VLAN/QoS metadata, or loses source-port extraction. Test CPU-injected packets to each port, extracted packets from each port, VLAN/QoS tagging, PTP one-step/two-step fields, and FDMA/manual extraction equivalence.
