# sources/distributed-fs/ceph-client/drivers/extcon/extcon-intel.h

## Purpose
`extcon-intel.h` defines the shared Intel USB-ID classification enum used by Intel PMIC extcon drivers.

## Important APIs, types, and functions
The sole API is `enum extcon_intel_usb_id` with values for OTG, grounded ID, floating ID, and ACA RID_A/RID_B/RID_C states.

## Control flow
There is no executable control flow. Intel PMIC drivers return these enum values from hardware-specific ID decoders and map them to host/device/charger behavior.

## State and persistence behavior
No runtime state is defined.

## Dependencies and integration points
It is included by `extcon-intel-cht-wc.c` and `extcon-intel-mrfld.c` to keep ID classification consistent across hardware variants.

## Risks and edge cases
Enum semantics must remain aligned with users. Adding values requires auditing switch statements in Intel extcon drivers.

## Test signals
Compile coverage of Intel extcon drivers and switch-case coverage for each enum value in role-detection tests.
