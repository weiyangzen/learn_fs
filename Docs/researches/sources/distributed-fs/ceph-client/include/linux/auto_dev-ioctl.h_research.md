# sources/distributed-fs/ceph-client/include/linux/auto_dev-ioctl.h

## Purpose
Kernel include wrapper for autofs device ioctl UAPI definitions. It keeps in-kernel includes under the `linux/` namespace while reusing the exported `uapi/linux/auto_dev-ioctl.h` contract.

## Important APIs, Types, And Functions
The header declares no new types or functions. Its effective API is all ioctl numbers, structs, and constants provided by `uapi/linux/auto_dev-ioctl.h`.

## Control Flow
There is no runtime control flow. Inclusion simply exposes the UAPI definitions to kernel code that manages autofs device-control ioctls.

## State And Persistence
No state is stored here. Persistent behavior belongs to the autofs device node, mount state, and userspace daemon protocol that consume the ioctl ABI.

## Dependencies And Integration Points
It depends directly on `uapi/linux/auto_dev-ioctl.h`. It integrates with autofs kernel code and userspace automount daemons that coordinate mount/expire operations through the device ioctl interface.

## Risks
The risk is ABI mismatch: this wrapper must not redefine or shadow UAPI structures. Any behavioral change should happen in the UAPI header and autofs implementation, not here.

## Test Signals
Build coverage is enough for the wrapper itself. Functional signals come from autofs ioctl tests and automount daemon integration that verifies kernel/userspace structure layout and ioctl numbers remain compatible.
