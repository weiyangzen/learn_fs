# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.h

## Purpose

`fman_memac.h` is the declaration header for the mEMAC backend. It exposes the mEMAC initialization entry point and pulls in shared MAC, netdevice, and fixed-PHY definitions needed by callers.

## Important APIs, Types, And Functions

The only API is `int memac_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params);`. `struct mac_device` is forward-declared, and shared MAC callback/config types are inherited from `fman_mac.h`.

## Control Flow

The generic MAC probing layer calls `memac_initialization()` after creating a `mac_device` and parsing device-tree parameters. The implementation fills operation callbacks, creates PCS/SerDes resources, initializes hardware, and registers FMan interrupts.

## State And Persistence Behavior

No state is stored here. Successful initialization leaves private mEMAC state attached to `mac_dev->fman_mac`.

## Dependencies And Integration Points

This header depends on `fman_mac.h`, Linux netdevice, and fixed PHY headers. It is included by the generic MAC layer when selecting an mEMAC implementation.

## Risks And Edge Cases

The header does not encode ownership, supported interfaces, or cleanup behavior; these are implementation contracts. Including fixed PHY and netdevice headers can increase compile dependencies for users that only need the function prototype.

## Test Signals

Compile mEMAC-enabled and disabled configurations. Probe-level tests should ensure the caller handles `-EPROBE_DEFER`, missing PCS, and other initialization errors returned through this single entry point.
