# sources/distributed-fs/ceph-client/include/linux/dsa/mv88e6xxx.h

## Purpose
This header defines special VLAN IDs used by Marvell mv88e6xxx DSA tagging.

## Important APIs, types, and functions
`MV88E6XXX_VID_STANDALONE` is `0`, and `MV88E6XXX_VID_BRIDGED` is `VLAN_N_VID - 1`. There are no functions.

## Control flow, state, and persistence
No runtime logic is present. The constants encode tagging/classification state for standalone and bridged ports.

## Dependencies and integration points
It includes `linux/if_vlan.h` for `VLAN_N_VID`. It is consumed by mv88e6xxx DSA tag and switch code.

## Risks and test signals
Risks include collision with user-configured VLANs and inconsistent handling between switch setup and tagger paths. Tests should cover standalone/bridged transitions and VLAN filtering interactions.
