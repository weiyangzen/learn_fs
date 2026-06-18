# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.h

## Purpose
This header declares the Linux ioctl, PCI lifecycle, module lifecycle, and in-kernel message dispatch functions for the AudioScience HPI driver.

## Important APIs, Types, And Functions
It declares `asihpi_adapter_probe()`, `asihpi_adapter_remove()`, `asihpi_init()`, `asihpi_exit()`, `asihpi_hpi_release()`, `asihpi_hpi_ioctl()`, and `hpi_send_recv()`. It also defines `HOWNER_KERNEL` as `(void *)-1`.

## Control Flow
There is no executable flow. The comments clarify that `hpi_send_recv()` is used by ALSA or other kernel callers when no file descriptor owner exists.

## State, Persistence, And Dependencies
No state is defined here. Callers must have `struct pci_dev`, `struct pci_device_id`, `struct file`, and HPI message/response types available.

## Integration Points
Included by the HPI Linux module glue and any in-kernel user that needs the exported HPI send/receive helper.

## Risks
`HOWNER_KERNEL` is a sentinel pointer and must never collide with a real file owner in owner-tracking code. The header has no include guard in this excerpt, so repeated inclusion depends on compiler tolerance for duplicate prototypes.

## Test Signals
Build coverage should ensure prototypes match implementation and kernel owner paths do not trigger user-owner cleanup errors.
