# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.h

## Purpose
Defines the user-visible ioctl ABI for the staging VME user-space access driver. It contains packed master/slave configuration structs, interrupt-generation arguments, ioctl command numbers, and the current limit of one configured bus.

## Important APIs, Types, and Constants
`VME_USER_BUS_MAX` limits module parameter handling to one bus. `struct vme_master` contains enable, VME base, size, address space, cycle flags, and data width. `struct vme_slave` contains enable, VME base, size, address space, and cycle flags. `struct vme_irq_id` carries an interrupt level and status/vector ID. IOCTLs are `VME_GET_SLAVE`, `VME_SET_SLAVE`, `VME_GET_MASTER`, `VME_SET_MASTER`, and `VME_IRQ_GEN`, all under magic `0xAE`.

## Control Flow and State
This header has no runtime logic. `vme_user.c` copies these packed structs to and from user space and translates them directly into VME framework calls.

## Dependencies and Integration Points
The structs use fixed-width `__u*` types and must stay compatible with user programs and compat ioctl handling. The constants mirror the legacy `/dev/bus/vme/*` ABI.

## Risks and Test Signals
Because structs are packed and contain 64-bit fields, ABI layout must be verified on 32-bit and 64-bit user space. The ABI exposes raw framework flag values, so mismatches with `vme.h` would break applications. Test with ioctl struct-size checks, compat users, invalid level/statid inputs, and get/set round trips for master and slave windows.
