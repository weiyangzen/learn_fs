# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.h

## Purpose

`sfh1_1/amd_sfh_init.h` declares the SFH 1.1 operation table used by the PCI driver.

## Important APIs, Types, and Functions

`struct amd_sfh1_1_ops` contains `init` and `toggle_hpd` callbacks. The header declares `amd_sfh1_1_init()` and `amd_sfh_toggle_hpd()`, then defines static `sfh1_1_ops` with those callbacks.

## Control Flow

`amd_sfh_pcie.c` stores `&sfh1_1_ops` in the PCI ID table for `PCI_DEVICE_ID_AMD_MP2_1_1`. Probe reads that driver data and schedules SFH 1.1 initialization instead of legacy MP2 initialization.

## State and Persistence Behavior

The operation table is static read-only data. Runtime state is carried by `amd_mp2_dev`.

## Dependencies and Integration Points

The header includes `amd_sfh_common.h` and bridges PCI probing to SFH 1.1 implementation files.

## Risks and Test Signals

Risks are callback signature drift and accidental omission from the PCI ID table. Test signals include build coverage and runtime probe selecting SFH 1.1 ops for device ID `0x164A`.
