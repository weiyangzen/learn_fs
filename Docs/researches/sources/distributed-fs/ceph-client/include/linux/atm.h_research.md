# sources/distributed-fs/ceph-client/include/linux/atm.h

## Purpose
Provides kernel-side inclusion of general ATM UAPI declarations and a compat ioctl structure.

## Important APIs, Types, And Functions
The header includes `uapi/linux/atm.h`. With `CONFIG_COMPAT`, `struct compat_atmif_sioc` mirrors ATM interface ioctl arguments using a compat user pointer.

## Control Flow, State, And Persistence
No runtime control flow or state is defined. It exists as a type bridge for ATM kernel code and compat ioctl handling.

## Dependencies And Integration Points
Depends on UAPI ATM definitions and `linux/compat.h` when compat is enabled. Integrated by ATM sockets, ATM device ioctl handlers, and 32-bit userspace compatibility on 64-bit kernels.

## Risks And Test Signals
Compat layout mismatches can break 32-bit ATM tools. Tests should cover native and compat ioctl argument translation, build coverage with/without `CONFIG_COMPAT`, and UAPI inclusion stability.
