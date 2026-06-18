# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.h

## Purpose
Declares shared Nitro Enclaves misc-device state used by the PCI and misc sides of the driver.

## APIs, Types, and Functions
Defines `struct ne_mem_region`, `struct ne_enclave`, `enum ne_state`, and `struct ne_devs`, and declares global `ne_devs`.

## Control Flow and State
No executable flow. The types describe persistent per-enclave state: memory-region list and pinned pages, event waitqueue and flag, max memory regions, mm ownership, vCPU masks, slot UID, NUMA node, threads-per-core masks, and state values `INIT`, `RUNNING`, and `STOPPED`.

## Dependencies and Integration
Includes `ne_pci_dev.h` and Linux cpumask/list/misc/mm/pci/wait primitives. `ne_pci_dev.c` updates enclave state on events; `ne_misc_dev.c` owns allocation and cleanup.

## Risks and Test Signals
Risk centers on shared state lifetime across PCI removal, enclave fd release, and event work. Tests should assert that all fields are initialized before list insertion and that event work cannot access freed enclave structures.
