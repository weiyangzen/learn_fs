# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/Makefile

## Purpose
Builds the Nitro Enclaves driver.

## APIs, Types, and Functions
`CONFIG_NITRO_ENCLAVES` builds module `nitro_enclaves.o` from `ne_pci_dev.o` and `ne_misc_dev.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
The misc-device source includes KUnit test code conditionally; both object files share headers and global `ne_devs`.

## Risks and Test Signals
Build with KUnit test enabled and disabled to ensure the static helper under test remains visible through inclusion.
