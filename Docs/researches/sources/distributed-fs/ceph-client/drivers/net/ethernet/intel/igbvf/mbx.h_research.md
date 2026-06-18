# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.h

## Purpose
`mbx.h` defines the PF/VF mailbox register bits, message encoding, timeouts, and the initialization prototype used by `igbvf`.

## Important APIs, Types, And Functions
The header exports `e1000_init_mbx_params_vf()`. It defines V2P mailbox bits such as `REQ`, `ACK`, `VFU`, `PFU`, `PFSTS`, `PFACK`, `RSTI`, and `RSTD`; message type modifiers `ACK`, `NACK`, and `CTS`; timeout constants; and VF-originated commands such as reset, set MAC address, set multicast, set VLAN, and set LPE.

## Control Flow
There is no executable flow. The constants drive mailbox state checks in `mbx.c` and command construction/parsing in `vf.c`.

## State And Persistence
No state is stored here. The constants define persistent protocol compatibility with the PF driver and hardware.

## Dependencies And Integration Points
The header includes `vf.h`, which creates a circular-looking but guarded local dependency between hardware type definitions and mailbox operation declarations. It is used by both `mbx.c` and `vf.c`.

## Risks
Protocol bit changes would break compatibility with PF mailbox handling. `E1000_VFMAILBOX_SIZE` constrains all command buffers, and the `MSGINFO` field is overloaded for command-specific metadata such as multicast count or add/remove operations.

## Test Signals
Compile tests catch missing symbols; runtime signals include successful VF reset ACK, MAC/VLAN/multicast command ACK/NACK behavior, and link CTS handling after PF resets.
