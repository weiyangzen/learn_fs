# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddi.h

## Purpose
`fddi.h` defines the basic FDDI address and MAC frame layout plus frame-control and frame-status indicator constants shared by SMT, hardware, and OS-specific paths.

## Important APIs, Types, And Functions
The central types are `struct fddi_addr` and `struct fddi_mac`. Constants include FDDI frame sizes (`FDDI_MAC_SIZE`, `FDDI_RAW_MTU`, `FDDI_RAW`), FC values for SMT, MAC, claim, beacon, sync/async LLC, and indicator bits (`C_INDICATOR`, `A_INDICATOR`, `E_INDICATOR`, `I_INDICATOR`, `L_INDICATOR`).

## Control Flow
There is no executable flow. Consumers use FC constants to classify received frames, construct SMT/MAC special frames, select sync versus async transmit queues, and interpret local/network indicators from the receive frame status.

## State And Persistence
No state is stored here. The header defines wire-format shapes and constants that must match FDDI frame encoding.

## Dependencies And Integration Points
Included by `smc.h`, CFM/ECM/ESS/FORBMAC files, SMT frame definitions, and hardware modules. `fplustm.c` uses `FC_CLAIM`, `FC_BEACON`, and `DBEACON_INFO`; `ess.c` uses `FC_SMT_INFO` and local indicators.

## Risks And Edge Cases
`struct fddi_mac` omits the FC byte and stores only destination, source, and payload, while some FORMAC paths prepend FC separately. Confusing canonical versus FDDI bit order is a recurring risk because address storage is handled outside this header.

## Test Signals
Frame parsing/building tests should confirm FC classification, max frame sizing, beacon/claim construction, local indicator handling, sync-bit queue selection, and multicast/group address detection through `GROUP_ADDR`.
