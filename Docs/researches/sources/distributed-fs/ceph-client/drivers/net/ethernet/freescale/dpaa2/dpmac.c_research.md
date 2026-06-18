# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.c

Purpose: Implements thin Linux-side wrappers for the DPAA2 DPMAC Management Complex commands. It opens/closes DPMAC sessions and exposes attributes, link state, counters, API version, protocol selection, and bulk statistics to MAC/phylink-facing DPAA2 code.

Important APIs, types, and functions: Exported functions are `dpmac_open()`, `dpmac_close()`, `dpmac_get_attributes()`, `dpmac_set_link_state()`, `dpmac_get_counter()`, `dpmac_get_api_version()`, `dpmac_set_protocol()`, and `dpmac_get_statistics()`. All use `struct fsl_mc_command`, `mc_encode_cmd_header()`, `mc_send_command()`, and payload definitions from `dpmac-cmd.h`.

Control flow: Each function zero-initializes an MC command, encodes the command ID, flags, and token into the header, fills command parameters where needed, sends the command, and unpacks response fields if the call succeeds. Open returns the session token from the response header. Attribute, counter, version, and statistics reads convert little-endian response fields into CPU values. Link-state set packs options, rate, `up`, `state_valid`, supported, and advertising fields.

State and persistence behavior: This file keeps no persistent state; the session token is returned to callers and used externally. Any effective state change, such as link state or protocol, is stored by MC firmware/hardware. Counter/statistic values are snapshots.

Dependencies and integration points: Depends on `linux/fsl/mc.h`, `dpmac.h`, and `dpmac-cmd.h`. It is consumed by DPAA2 MAC support, switch port endpoint connection, and Ethernet drivers that need to synchronize phylink/MAC state with DPMAC objects.

Risks: MAC addresses are not handled here, but all other fields depend on exact MC ABI layout and endian conversion. `dpmac_get_counter()` writes `dpmac_cmd->id = id` without explicit width conversion because the field is one byte; enum expansion would matter if IDs exceed u8. Bulk statistics requires caller-provided DMA IOVAs for counter IDs and output values; invalid mapping/lifetime is a caller risk not checked here. Link-state bitfields rely on a zeroed command buffer because setters OR bits into `state`.

Test signals: DPMAC open/close token lifecycle, attribute read against known DPMAC IDs, link up/down and advertised capability propagation through phylink, individual counter reads, API version query, protocol reconfiguration on supported links, bulk statistics with valid and invalid DMA buffers, and MC error propagation for stale tokens or removed endpoints.
