# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_sdp.c

## Purpose

`rvu_sdp.c` identifies SDP PF/VF functions and manages SDP channel information in the RVU AF. It supports both firmware-provided channel data and PCI discovery of SDP PF devices, then serves mailbox requests that set or retrieve SDP channel ranges used by NIX/SDP traffic paths.

## Important APIs, Types, And Functions

- `PCI_DEVID_OTX2_SDP_PF`, `RVU_SDP_VF_DEVID`, `MAX_SDP`, and static `sdp_pf_num[]` define recognized SDP devices.
- `is_sdp_pfvf()` checks whether a pcifunc belongs to a discovered SDP PF.
- `is_sdp_pf()` distinguishes the PF function from its VFs.
- `is_sdp_vf()` handles both RVU VF-device-id based SDP VFs and VFs under discovered SDP PFs.
- `rvu_sdp_init()` discovers SDP PFs or consumes firmware channel data and attaches `sdp_node_info` storage to `struct rvu_pfvf`.
- `rvu_mbox_handler_set_sdp_chan_info()` copies PF-provided SDP channel metadata into the AF-side PF/VF state.
- `rvu_mbox_handler_get_sdp_chan_info()` returns fixed legacy SDP channel ranges or programmable channel data from hardware.

## Control Flow

Initialization first checks `rvu->fwdata->channel_data.valid`. If valid, PF 0 is treated as SDP, and its `sdp_info` pointer aliases firmware channel info. Otherwise it scans PCI devices with Cavium vendor id and the SDP PF device id, derives the RVU PF number from `pdev->bus->number - 1`, allocates `struct sdp_node_info` for each discovered PF, stores the PF number in `sdp_pf_num[]`, and releases the final PCI reference.

Mailbox set-channel-info simply finds the requester PF/VF state and copies the supplied `sdp_node_info`. Mailbox get-channel-info checks `hw->cap.programmable_chans`: legacy hardware returns `NIX_CHAN_SDP_CH_START` and `NIX_CHAN_SDP_NUM_CHANS`; programmable hardware reads the first NIX block `NIX_AF_CONST1` low 12 bits for channel count and uses `hw->sdp_chan_base`.

## State And Persistence

State is process-local/static in `sdp_pf_num[]` and per-RVU in `rvu->pf[pf].sdp_info`. The firmware-data path points directly at firmware channel data; the PCI-discovery path allocates devm-managed memory. Channel info is not persisted outside AF memory, and hardware channel counts come from NIX registers.

## Dependencies And Integration Points

The file depends on PCI core discovery, RVU pcifunc helpers, firmware data in `rvu->fwdata`, `struct sdp_node_info`, and NIX constants/register reads. NIC and AF paths use `is_sdp_*()` to special-case SDP representor or SDP function behavior, including scheduler/channel setup in `otx2_common.c`.

## Risks

- The PF-number derivation from PCI bus number is platform-specific and can break if bus numbering changes.
- `sdp_pf_num[]` is static module-global; multiple RVU devices would share discovery state.
- Firmware path assumes PF 0 is SDP and does not allocate a private copy of channel info.
- `set_sdp_chan_info()` assumes `pfvf->sdp_info` is non-null; malformed ordering of mailbox calls could dereference a null pointer.

## Test Signals

Probe on firmware-channel-data and PCI-discovery platforms, `is_sdp_pf()`/`is_sdp_vf()` pcifunc tests, SDP mailbox set/get, programmable versus fixed channel hardware, and SDP representor datapath setup are the most useful signals. Fault injection should cover missing allocation and absent SDP PCI devices.
