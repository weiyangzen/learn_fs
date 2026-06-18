# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devids.h

## Purpose

`i40e_devids.h` defines PCI device IDs recognized by the i40e driver for XL710, X710, XXV710, X722, QEMU, N3000, backplane, QSFP, SFP, SFP28, and Base-T variants.

## Important APIs, Types, And Functions

- Device ID macros include `I40E_DEV_ID_SFP_XL710`, `I40E_DEV_ID_QEMU`, `I40E_DEV_ID_QSFP_*`, `I40E_DEV_ID_10G_BASE_T*`, `I40E_DEV_ID_25G_*`, and X722 variants.
- `I40E_IS_X710TL_DEVICE(d)` groups 1G/5G/10G Base-T backplane controller IDs for X710-TL handling.

## Control Flow

The header has no runtime control flow. Other driver tables and conditional paths include it to match PCI IDs and classify device variants.

## State And Persistence

No state is owned. These constants influence probe-time device matching and feature/device-family branching elsewhere in the driver.

## Dependencies And Integration Points

It is a standalone header consumed by PCI ID tables and hardware-variant logic in the i40e driver.

## Risks

- Missing or wrong IDs prevent devices from binding or can route them through incorrect variant handling.
- The grouping macro must stay aligned with hardware errata and feature differences for X710-TL devices.

## Test Signals

Probe tests on each supported PCI ID, static review against Intel device ID lists, and build checks for PCI ID table references are the main signals.
