<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h

## Purpose
Defines ATM device-driver control ABI: interface statistics, link rates, address/ESI management, loopback controls, backend selection, and VC state/change constants.

## Important APIs, Types, And Functions
Exports PCR constants, `atm_aal_stats`, `atm_dev_stats`, many `ATM_*` ioctls for interface names/type/ESI/address/CIRANGE/stat/loopback/backend/party operations, backend ids, loopback bit masks, `atm_iobuf`, `atm_cirange`, single-copy flags, modify-QoS flags, and VC state text maps.

## Control Flow
Management tools issue ATM interface ioctls through `atmif_sioc` or `atm_iobuf` to discover devices, configure addressing/ranges/ESI, read stats, set loopback, select backends, and manage point-to-multipoint parties.

## State And Persistence
State includes interface addresses, ESI, connection identifier range, loopback mode, stats, backend bindings, and VC flags. It is runtime driver/network state.

## Dependencies And Integration Points
Depends on ATM API/core/ioctl headers. Integrates with ATM drivers, CLIP/LANE/MPOA/PPP/BR2684 backends, signaling daemons, and diagnostic tools.

## Risks And Edge Cases
Read-and-zero stats, `void __user *` buffer lengths, loopback local/remote combination constraints, backend id coordination, and legacy ioctl number ranges are sensitive.

## Test Signals
Interface discovery, address add/del/reset, ESI set/force, stats get/get-zero, loopback set/query, backend attach, party add/drop, and malformed buffer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h -->
