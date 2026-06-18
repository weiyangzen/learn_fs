# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.c

## Purpose
Implements the brcmfmac BCDC protocol backend used by SDIO and USB FullMAC transports. It formats dongle control commands, wraps data packets in BCDC headers, integrates firmware-signaling flow control, and installs protocol callbacks into `drvr->proto`.

## Important APIs, Types, and Functions
Defines `struct brcmf_proto_bcdc_dcmd`, `struct brcmf_proto_bcdc_header`, and private `struct brcmf_bcdc`. Public functions are `drvr_to_fws()`, `brcmf_proto_bcdc_txflowblock()`, `brcmf_proto_bcdc_txcomplete()`, `brcmf_proto_bcdc_attach()`, and `brcmf_proto_bcdc_detach()`. Callback helpers include query/set dcmd, control-message completion, header push/pull, queued data TX, direct data TX, interface add/delete/reset, RX reorder, init-done, and debugfs creation.

## Control Flow, State, and Persistence
Control requests increment a 16-bit request id, fill the BCDC dcmd header with command, length, set/query flag, and interface index, send via `brcmf_bus_txctl()`, then loop on `brcmf_bus_rxctl()` until the matching id arrives or retries fail. Data TX pushes a 4-byte BCDC header with protocol version, checksum hints, priority, interface index, and firmware-signal offset before bus TX. RX validates length, version, interface mapping, checksum flag, priority, and data offset, optionally lets firmware signaling consume headers, and returns the target `brcmf_if`. Attach allocates `struct brcmf_bcdc`, verifies the control message buffer layout, assigns protocol callbacks, grows `drvr->hdrlen`, and sets bus control max length. Detach tears down firmware signaling and frees state.

## Dependencies and Integration Points
Depends on brcmfmac bus control/data APIs, fwsignal, proto core, tracepoints, debug, cfg interface lookup, skbuff helpers, and firmware iovar/dcmd semantics. It is selected by SDIO/USB Kconfig.

## Risks and Test Signals
Risks include request-id mismatch, stale control responses, header offset underflow/overpull, missing interface lookup, flow-control deadlock, and checksum flag misuse. Test control get/set commands, multi-interface data RX/TX, firmware signaling on/off, bus flow block/unblock, TX completion paths, and malformed short/non-BCDC packets.
