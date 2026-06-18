# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_common.h

## Purpose

`amd_sfh_common.h` defines shared MP2/SFH constants, device state, command IDs, sensor information structures, and the operation table used between PCI transport, HID client, and descriptor backends.

## Important APIs, Types, and Functions

Important constants include AMD MP2 PCI device IDs, C2P/P2C message-register address macros for register revisions, sensor status values, and `AMD_SFH_IDLE_LOOP`. `struct amd_mp2_sensor_info` carries sensor ID, polling period, and DMA address. `struct sfh_dev_status` tracks HPD, ALS, and SRA availability. `struct amd_mp2_dev` is the central persistent device object. `struct amd_mp2_ops` contains callbacks for start/stop, response, interrupts, discovery, power management, removal, descriptor lookup, and report generation. Inline helpers `amd_get_c2p_val()` and `amd_get_p2c_val()` select register maps based on `mp2->rver`.

## Control Flow

There is no direct control flow in the header, but the callback table defines it: PCI probe selects or installs `amd_mp2_ops`; client initialization calls descriptor and sensor callbacks; HID request paths call report callbacks.

## State and Persistence Behavior

`struct amd_mp2_dev` persists for the PCI device lifetime and owns the PCI device pointer, MMIO mappings, SFH 1.1 virtual sensor memory base, operation tables, input-data arrays, active-control status, feature flags, work item, mutex, initialization flag, and register revision.

## Dependencies and Integration Points

The header depends on PCI, mutexes, and local HID state from `amd_sfh_hid.h`. It is included by nearly every AMD SFH source file and is the contract that lets legacy MP2 and SFH 1.1 implementations share the HID client.

## Risks and Test Signals

Changing callback semantics affects all SFH generations. Register-map helpers must match firmware/CPU revision behavior. Test signals include compile coverage of all SFH objects, runtime validation on both `PCI_DEVICE_ID_AMD_MP2` and `PCI_DEVICE_ID_AMD_MP2_1_1`, and suspend/resume paths that exercise installed ops.
