<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm.h

## Purpose
Defines the general Linux ATM socket ABI: cell constants, AAL protocol ids, socket-option encoding, traffic/QoS parameters, PVC/SVC addresses, address-use helpers, and ATM ioctl wrapper structs.

## Important APIs, Types, And Functions
Important exports include ATM cell/PDU limits, AAL constants, `SO_ATMQOS`, `SO_ATMSAP`, `SO_ATMPVC`, `struct atm_trafprm`, `struct atm_qos`, `struct sockaddr_atmpvc`, `struct sockaddr_atmsvc`, `atmsvc_addr_in_use`, `atmpvc_addr_in_use`, `struct atmif_sioc`, and `atm_backend_t`.

## Control Flow
ATM applications create ATM sockets, set QoS/SAP options, bind or connect PVC/SVC addresses, and use ATM-specific ioctls for interface/device/backend configuration. Helpers identify whether PVC/SVC addresses are populated.

## State And Persistence
Socket state includes QoS, SAP, PVC/SVC address, AAL, and multipoint/backend choices. Interface and backend state is managed by related ATM ioctls and daemons.

## Dependencies And Integration Points
Depends on ATM API alignment, SAP and ioctl headers, Linux types, and compiler user-pointer annotations. Integrates with ATM socket families, signaling daemon, CLIP/LANE/MPOA/PPPoATM/BR2684 backends, and legacy ATM drivers.

## Risks And Edge Cases
Socket option bit encoding reserves limited level bits, ABI alignment differs on sparc/ia64, VPI/VCI magic values include negative sentinels, and traffic parameter bitfields must match userspace expectations.

## Test Signals
ATM socket option get/set tests, PVC/SVC bind/connect tests, QoS encoding validation, address helper behavior, and ABI alignment tests on affected architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm.h -->
