<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c

## Purpose
PCI parent driver for Intel Elkhart Lake Programmable Service Engine I/O. It enumerates a PCI function and creates auxiliary devices for PSE GPIO and timed I/O.

## Important APIs, Types, And Functions
`ehl_pse_io_dev_create()` allocates `struct ehl_pse_io_data`, slices BAR0 into 4 KiB resources per child, assigns MSI vectors by index, and calls `__devm_auxiliary_device_create()` using names from `linux/ehl_pse_io_aux.h`.

## Control Flow
Probe enables the PCI device with pcim, sets bus mastering, allocates exactly two MSI vectors, creates GPIO child index 0, and creates TIO child index 1. The actual functionality is in auxiliary drivers.

## State And Persistence
Only child-device platform data and PCI MSI allocation are maintained. Devm/pcim clean up on remove.

## Dependencies And Integration Points
Depends on PCI, auxiliary bus, BAR0 resources, MSI, and the public EHL PSE I/O auxiliary header contract.

## Risks And Test Signals
Risks include assuming BAR layout and exactly two vectors, and creating children with invalid IRQ vectors if allocation changes. Test PCI probe on device IDs `0x4b88` and `0x4b89`, child auxiliary driver binding, resource ranges, and interrupt delivery for both children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c -->
