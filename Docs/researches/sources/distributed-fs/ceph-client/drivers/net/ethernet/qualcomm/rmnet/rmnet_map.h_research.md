# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map.h

Purpose: Defines RMNET MAP command metadata and declares MAP data, checksum, deaggregation, command, and uplink aggregation helpers.

Important APIs and types: `struct rmnet_map_control_command` models MAP command payloads after the MAP header, including command name/type, transaction id, and flow-control fields. `enum rmnet_map_commands` names supported commands, mainly flow enable/disable. Command response constants define ACK, unsupported, and invalid types. Function declarations cover `rmnet_map_deaggregate()`, `rmnet_map_add_map_header()`, `rmnet_map_command()`, downlink and uplink checksum helpers, MAPv5 next-header processing, and TX aggregation lifecycle/configuration.

Control flow and integration: `rmnet_handlers.c` calls the ingress, egress, checksum, deaggregation, and aggregation helpers declared here. `rmnet_map_command.c` consumes the control command structure. `rmnet_map_data.c` implements data-plane helpers and aggregation configuration.

State and persistence: This header defines no global state. It standardizes command layout and helper contracts for state stored in `struct rmnet_port`, `struct rmnet_priv`, and SKBs.

Risks and test signals: Bitfield layout and alignment of `rmnet_map_control_command` are protocol-sensitive. Tests should cover command parsing, mux id routing, checksum offload variants, and padding/header length invariants. Build tests should catch prototype drift across MAP files.
