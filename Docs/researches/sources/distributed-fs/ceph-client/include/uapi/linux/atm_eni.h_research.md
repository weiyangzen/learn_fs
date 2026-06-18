<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h

## Purpose
Defines ENI ATM driver-specific utility ioctls and buffer multiplier structure.

## Important APIs, Types, And Functions
`struct eni_multipliers` carries transmit and receive buffer multipliers in percent. `ENI_MEMDUMP` requests a memory map dump and `ENI_SETMULT` sets buffer multipliers using `atmif_sioc`.

## Control Flow
Driver-specific utilities issue private SAR ioctls on an ATM interface, passing an `atmif_sioc` that points to ENI-specific data when needed.

## State And Persistence
State is live ENI driver buffer configuration and diagnostic output. It is not persistent across driver reload/reset unless tooling reapplies it.

## Dependencies And Integration Points
Depends on `atmioc.h` and `atmif_sioc` from `atm.h`. Integrates with ENI SAR driver internals and ATM diagnostics.

## Risks And Edge Cases
Multipliers must be greater than 100 per comment; invalid user pointers and driver-private ioctl collisions are risks.

## Test Signals
Private ioctl availability, multiplier validation, memory dump path smoke tests, and malformed `atmif_sioc` rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h -->
