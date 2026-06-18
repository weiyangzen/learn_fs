# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.c

## Purpose
`proto.c` is the protocol dispatcher for `brcmfmac`. It allocates the generic `struct brcmf_proto`, selects the concrete firmware protocol implementation based on the bus-advertised `proto_type`, verifies that required callbacks were installed, and detaches the selected implementation during teardown.

## Important APIs, types, and functions
- `brcmf_proto_attach(struct brcmf_pub *drvr)` allocates `drvr->proto`, dispatches to `brcmf_proto_bcdc_attach()` for `BRCMF_PROTO_BCDC` or `brcmf_proto_msgbuf_attach()` for `BRCMF_PROTO_MSGBUF`, validates mandatory handlers, and returns `0` or `-ENOMEM`.
- `brcmf_proto_detach(struct brcmf_pub *drvr)` calls the matching BCDC/MSGBUF detach routine and frees `drvr->proto`.
- Required handlers checked here include `tx_queue_data`, `hdrpull`, `query_dcmd`, `set_dcmd`, `configure_addr_mode`, `delete_peer`, `add_tdls_peer`, and `debugfs_create`.

## Control flow
Attach is called after bus setup but before normal network operation. The bus backend sets `drvr->bus_if->proto_type`; `proto.c` uses that value to attach protocol-specific state and function pointers. If protocol type is unsupported or any required callback remains unset, it logs an error, frees the generic proto object, clears `drvr->proto`, and fails. Detach mirrors the type dispatch and releases protocol-specific then generic state.

## State and persistence behavior
The only state owned here is the heap-allocated `struct brcmf_proto` stored in `drvr->proto`. Concrete protocol modules may place private data in `proto->pd`. This state persists for the `brcmf_pub` lifetime and is not persisted externally.

## Dependencies and integration points
The file depends on `core.h`, `bus.h`, `proto.h`, `bcdc.h`, and `msgbuf.h`. It integrates SDIO/USB-style BCDC buses and PCIe MSGBUF buses with the common core through a single vtable consumed by inline wrappers in `proto.h`.

## Risks and edge cases
- All attach failures return `-ENOMEM`, even unsupported protocol type or missing handler cases, which can obscure root cause.
- The required-callback check covers only mandatory fields. Optional callbacks must be NULL-safe at call sites.
- Because protocol choice comes from bus state, a bus backend that sets the wrong `proto_type` can attach the wrong implementation or fail late.

## Test signals
Test by probing both BCDC and MSGBUF bus types, validating required callbacks are populated, forcing unsupported `proto_type`, injecting attach failures in concrete protocols, and ensuring detach frees `drvr->proto` without leaking or double-detaching.
