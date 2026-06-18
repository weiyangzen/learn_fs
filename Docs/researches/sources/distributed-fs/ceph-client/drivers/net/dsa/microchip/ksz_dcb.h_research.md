# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.h

## Purpose
`ksz_dcb.h` declares the DCB support functions used by the KSZ common DSA driver. It exposes per-port priority and apptrust operations plus global and per-port initialization hooks.

## Important APIs, Types, and Functions
The header declares DSA-facing callbacks for default priority, DSCP priority add/delete/get, apptrust set/get, `ksz_dcb_init_port()`, and `ksz_dcb_init()`. It includes `net/dsa.h` and `ksz_common.h` so functions can operate on `struct dsa_switch` and `struct ksz_device`.

## Control Flow
There is no local control flow. `ksz_common.c` installs these functions into `ksz_switch_ops` and calls the init helpers during switch setup and user-port setup.

## State and Persistence
The header defines no state. State is managed by `ksz_dcb.c` through hardware registers selected from `struct ksz_device` chip data.

## Dependencies and Integration Points
This is the coupling point between the common driver and the DCB implementation. Any build unit using these declarations needs the KSZ private structures and DSA definitions.

## Risks and Edge Cases
Because the prototypes are unconditional, build configurations must compile `ksz_dcb.c` whenever `ksz_common.c` references DCB callbacks. Signature drift would break DSA ops initialization at compile time.

## Test Signals
Compile with the Microchip KSZ DSA driver enabled and confirm `ksz_switch_ops` resolves all DCB symbols. Runtime DCB behavior should be validated through the implementation file's test signals.
