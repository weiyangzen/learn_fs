# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/core.c

## Purpose
Provides BCA-specific firmware-vendor operations for brcmfmac Broadcom AP chipsets.

## Important APIs, Types, and Functions
`brcmf_bca_feat_attach()` clears `BRCMF_FEAT_SAE` because SAE support is not confirmed. `brcmf_bca_alloc_fweh_info()` allocates `struct brcmf_fweh_info` with `BRCMF_BCA_E_LAST` event handler slots and stores it in `drvr->fweh`. `brcmf_bca_ops` publishes these callbacks as `struct brcmf_fwvid_ops`.

## Control Flow, State, and Persistence
Feature attach mutates driver feature flags after interface setup. Event allocation creates driver-owned event-handler state sized for BCA firmware event codes and persists in `drvr->fweh` until normal driver cleanup.

## Dependencies and Integration Points
Depends on brcmfmac core, bus, fwvid, feature, and flexible allocation helpers. It is registered by `module.c` for `BRCMF_FWVENDOR_BCA` or linked directly in built-in configurations through the parent Makefile.

## Risks and Test Signals
Risks include disabling SAE unnecessarily, event-code table size mismatch with firmware, and allocation failure paths. Test BCA firmware probe, event delivery near high event codes, feature negotiation, and WPA3/SAE capability exposure.
