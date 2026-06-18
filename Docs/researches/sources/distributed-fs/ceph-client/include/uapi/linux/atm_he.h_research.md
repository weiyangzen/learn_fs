<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h

## Purpose
Defines FORE/HE ATM driver-specific register access ioctl structures and register type constants.

## Important APIs, Types, And Functions
`HE_GET_REG` is a private SAR ioctl. `struct he_ioctl_reg` carries register address, value, and type. Register types include PCI, RCM, TCM, and mailbox.

## Control Flow
Diagnostic utilities pass an `atmif_sioc` to `HE_GET_REG`; the driver interprets the pointed data as `he_ioctl_reg`, reads the requested register class/address, and returns the value.

## State And Persistence
No persistent state is defined. Register reads observe live hardware state.

## Dependencies And Integration Points
Depends on ATM ioctl numbering and `atmif_sioc`. Integrates with HE ATM hardware diagnostics.

## Risks And Edge Cases
Raw register access can expose hardware details; invalid register type/address and user buffer sizing must be checked.

## Test Signals
Known register read tests, invalid type/address rejection, and compat pointer handling through `atmif_sioc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h -->
