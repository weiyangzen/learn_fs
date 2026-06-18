# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_common.h

## Purpose
`dst_common.h` is the shared DST frontend/CA contract. It defines device type constants, feature flags, tuner flags, GPIO/PIO command values, communication constants, the central `struct dst_state`, board/tuner descriptor structs, and exported function prototypes.

## Important APIs, Types, And Functions
Important constants include `DST_TYPE_IS_SAT/TERR/CABLE/ATSC`, type flags such as `DST_TYPE_HAS_TS188`, `DST_TYPE_HAS_TS204`, `DST_TYPE_HAS_FW_*`, `DST_TYPE_HAS_MULTI_FE`, and `DST_TYPE_HAS_VLF`, capability flags such as `DST_TYPE_HAS_CA`, `DST_TYPE_HAS_DISEQC*`, and `DST_TYPE_HAS_ANALOG`, tuner flags, RDC 8820 GPIO values, `GET_REPLY`, `GET_ACK`, `FIXED_COMM`, and `ACK`. Major types are `struct dst_state`, `struct tuner_types`, `struct dst_types`, and `struct dst_config`.

## Control Flow
The header does not execute, but `struct dst_state` is passed through all frontend and CA operations. Its fields are filled during `dst_probe()`, read and updated during tuning/status calls, shared with CA ioctls, and freed in the frontend release callback. Prototypes expose the low-level communication helpers across `dst.c` and `dst_ca.c`.

## State And Persistence
`struct dst_state` contains the entire runtime state for a DST frontend: bridge/I2C/config pointers, frontend object, tx/rx buffers, detected device type/capability flags, current tuning and DiSEqC parameters, decoded signal metrics, message buffers, identity strings, mutex, firmware name, and optional CA device. It is volatile kernel memory only.

## Dependencies And Integration Points
The header depends on DVB frontend and device types, Linux mutexes, local `bt878.h`, and `dst_ca.h`. It is the integration point between `dvb-bt8xx`, `dst.c`, and `dst_ca.c`.

## Risks
Many flags use overlapping bit values in separate namespaces (`type_flags`, `dst_hw_cap`, tuner types), so using a flag in the wrong field can silently misconfigure behavior. Fixed-size buffers such as `tx_tuna[10]`, `rxbuffer[10]`, `messages[256]`, and short identity strings require strict length discipline in protocol code. Exposing communication helpers means CA and frontend code must coordinate locking around `dst_mutex`.

## Test Signals
Compile coverage across DST modules, correct board-type detection, correct frontend ops selection, CA attachment for CA-capable cards, and valid signal/tuning state transitions all validate this shared contract.
