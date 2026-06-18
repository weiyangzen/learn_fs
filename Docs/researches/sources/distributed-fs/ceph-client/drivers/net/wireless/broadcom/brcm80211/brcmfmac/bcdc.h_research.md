# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bcdc.h

## Purpose
Declares the BCDC protocol attach/detach and TX completion/flow-control entry points, with stubs when BCDC is not compiled.

## Important APIs, Types, and Functions
When `CONFIG_BRCMFMAC_PROTO_BCDC` is enabled, exposes `brcmf_proto_bcdc_attach()`, `brcmf_proto_bcdc_detach()`, `brcmf_proto_bcdc_txflowblock()`, `brcmf_proto_bcdc_txcomplete()`, and `drvr_to_fws()`. Disabled builds get no-op attach/detach stubs.

## Control Flow, State, and Persistence
No state in the header. Runtime BCDC protocol state lives in `struct brcmf_bcdc` allocated by `bcdc.c`.

## Dependencies and Integration Points
Used by brcmfmac protocol selection and bus code that calls BCDC TX completion/flow-control callbacks.

## Risks and Test Signals
Risks are missing prototypes in non-BCDC builds and conditional compilation mismatch. Test SDIO/USB BCDC builds and PCIE/MSGBUF-only builds.
