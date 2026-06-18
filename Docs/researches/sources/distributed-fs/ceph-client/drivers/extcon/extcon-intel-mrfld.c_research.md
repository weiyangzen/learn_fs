# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel-mrfld.c

## Purpose
`extcon-intel-mrfld.c` reports USB host role and charger-related extcon capabilities for Intel Merrifield Basin Cove PMIC power-source hardware.

## Important APIs, types, and functions
`struct mrfld_extcon_data` stores device, regmap, extcon device, cached charger IRQ status, and PMIC ID. Important functions are `mrfld_extcon_get_id()`, `mrfld_extcon_role_detect()`, `mrfld_extcon_cable_detect()`, `mrfld_extcon_interrupt()`, and `mrfld_extcon_sw_control()`.

## Control flow
Probe gets the parent PMIC regmap and IRQ, registers extcon cables, requests a shared threaded IRQ, reads PMIC revision, enables software control, detects initial USB role, caches current charger IRQ status, unmasks charger/USB-ID interrupts, enables USB-ID detection, and stores driver data. IRQ handling compares current `BCOVE_SCHGRIRQ1` status against the cached status because firmware clears the normal IRQ register, runs role detection on USB-ID changes, updates the cache, and clears the PMIC top-level charger interrupt mask.

## State and persistence behavior
State is runtime-only: cached status, PMIC revision, extcon states, and PMIC control bits. Remove disables software control.

## Dependencies and integration points
The driver depends on Intel SoC PMIC MFD/regmap definitions, Basin Cove register definitions, extcon provider APIs, IRQs, and the shared Intel USB-ID enum from `extcon-intel.h`.

## Risks and edge cases
PMIC A0 and B0 invert/interpret the ground bit differently, so revision-specific logic is required. Firmware clearing IRQ registers forces cached-status comparison and can miss events if cache synchronization is wrong. The cable list includes charger types, but this implementation only updates host state. Interrupt return is `IRQ_NONE` on no detected status change.

## Test signals
Test PMIC A0/B0 ID decoding, ID ground/float/RID_A/B/C states, cached status changes, interrupt clearing, software-control enable/disable, and no-change IRQ behavior.
