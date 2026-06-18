# sources/distributed-fs/ceph-client/drivers/edac/i82975x_edac.c Research

## Purpose
`i82975x_edac.c` is the EDAC driver for Intel 82975X DDR2 memory controllers. It maps the MCHBAR register space, verifies ECC is enabled, detects symmetric dual-channel configurations, initializes DIMM/csrow metadata from channel DRB registers, and polls PCI ECC status/address/syndrome registers.

## Important APIs, Types, and Functions
`struct i82975x_pvt` holds the mapped MCHBAR window. `struct i82975x_error_info` captures `ERRSTS`, `EAP`, `XEAP`, `DES`, syndrome, second `ERRSTS`, and derived channel data. `i82975x_get_error_info()` snapshots PCI status and detail registers and clears CE/UE bits. `i82975x_process_error_info()` constructs the page from cache-line-granular EAP plus XEAP bit 32, finds the EDAC row, derives channel from EAP bit 0 when dual-channel, calculates offset within the page using DIMM grain, and reports UE or CE.

`dual_channel_active()` compares channel 0 and 1 DRB values to treat only interleaved-symmetric layouts as dual-channel. `i82975x_init_csrows()` reads cumulative DRB boundaries from MCHBAR, scales them by 32 MiB and channel count, labels DIMMs `DIMM A/B`, and fills DDR2/SECDED/x8 metadata. `i82975x_probe1()` maps MCHBAR, checks per-channel DRC ECC state, allocates EDAC topology, initializes rows, marks hardware scrub support, clears stale errors, and registers the MC.

## Control Flow
Module init initializes opstate, registers the PCI driver, and can fallback to a manual host-bridge lookup. Probe enables the PCI device, maps MCHBAR, rejects disabled ECC, registers EDAC, and returns. Polling runs `i82975x_check()`. Remove deletes the EDAC MC, unmaps MCHBAR, and frees the MC object. Module exit unregisters the PCI driver and conditionally calls manual removal when the fallback path was used.

## State and Persistence
State is kernel-only: mapped MCHBAR, EDAC MC/DIMM metadata, global `mci_pdev`, and `i82975x_registered`. Hardware error bits are cleared on every snapshot. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on PCI config space, `ioremap`, EDAC MC APIs, Intel 82975X PCI IDs, and EDAC opstate configuration. It does not create generic EDAC PCI control unlike some older sibling drivers.

## Risks and Edge Cases
The EDAC layer sizing is unusual: it sets chip-select size to all DIMMs and channel size to `I82975X_NR_CSROWS(chans)`, so topology assumptions need hardware validation. Mixed asymmetric memory is treated as single-channel for channel attribution. The driver assumes ECC requires x8 devices and hardcodes SECDED. Error snapshots are racy, and MCHBAR must already be enabled by firmware. Fallback registration state is easy to mishandle.

## Test Signals
Signals include successful MCHBAR mapping, ECC-disabled rejection, DIMM labels and row sizes matching DRB registers, correct CE/UE reports including XEAP high-address cases, correct single-vs-dual-channel detection on asymmetric layouts, and clean unmap/free on unload.
