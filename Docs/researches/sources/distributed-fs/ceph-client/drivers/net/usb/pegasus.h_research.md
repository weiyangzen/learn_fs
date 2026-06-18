# sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.h

## Purpose
`pegasus.h` provides Pegasus hardware constants and the source USB device table. It is intentionally double-included: normal inclusion defines constants/types, while inclusion with `PEGASUS_DEV` macros expands supported products.

## Important APIs, Types, And Constants
Feature flags include `PEGASUS_II` and `HAS_HOME_PNA`; runtime bits include `PEGASUS_UNPLUG` and `PEGASUS_RX_URB_FAIL`. Register constants cover Ethernet control, EEPROM, PHY, USB/status, wakeup, GPIO, and Pegasus II-specific registers. USB requests include `PEGASUS_REQ_GET_REGS` and `PEGASUS_REQ_SET_REGS`.

`pegasus_t` stores USB/netdev pointers, MII info, runtime and feature flags, message level, WoL options, device-table index, interrupt interval, tasklet/work, RX/TX/interrupt URBs, RX SKB, fixed TX buffer, cached Ethernet regs, PHY ID, and GPIO reset value. `struct usb_eth_dev` binds product name, vendor, product, and private flags.

## Control Flow
`pegasus.c` includes the file normally, then includes it again under macros to build `usb_dev_id[]` and `pegasus_ids[]`. Product feature flags drive reset GPIO programming, Pegasus II setup, HomePNA/MII mode handling, and board quirks. `PEGASUS_DEV_CLASS` handles IDs that need class-sensitive matching.

## State And Persistence Behavior
The header has no executable state, but its product list becomes compiled module state and its flags become per-device runtime behavior. Constants define EEPROM, PHY, GPIO, Ethernet control, and wake register state.

## Dependencies And Integration Points
It is tightly coupled to `pegasus.c` and depends on surrounding kernel definitions for USB, netdev, MII, tasklet/work, URB, SKB, and integer types.

## Risks And Test Signals
The double-include product list is compact but fragile. USB ID collisions require class-sensitive entries or blacklist logic. Tests should verify every generated USB ID maps to a `usb_eth_dev` entry, quirks select correct GPIO/Pegasus II behavior, HomePNA/MII flags work, and dynamic `devid` extension remains within sentinel space.
