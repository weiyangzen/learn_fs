# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_misc_dev.c

## Purpose
Implements the user-facing Nitro Enclaves misc device and per-enclave anonymous file API. It manages CPU-pool donation, enclave slot creation, vCPU assignment, hugetlb memory registration, enclave start, event polling, and cleanup.

## APIs, Types, and Functions
Global API is `/dev/nitro_enclaves` with `NE_CREATE_VM`, returning an anon inode using `ne_enclave_fops`. Enclave ioctls are `NE_ADD_VCPU`, `NE_GET_IMAGE_LOAD_INFO`, `NE_SET_USER_MEMORY_REGION`, and `NE_START_ENCLAVE`. Major helpers include `ne_setup_cpu_pool()`, `ne_teardown_cpu_pool()`, `ne_set_kernel_param()`, CPU selection/check helpers, `ne_set_user_memory_region_ioctl()`, `ne_merge_phys_contig_memory_regions()`, `ne_start_enclave_ioctl()`, `ne_enclave_release()`, and `ne_create_vm_ioctl()`.

## Control Flow and State
Module init initializes the CPU-pool mutex and registers the NE PCI driver. The `ne_cpus` module parameter, settable only by `CAP_SYS_ADMIN`, parses a CPU list, requires online CPUs from one NUMA node, excludes CPU0 and siblings, requires full cores, offlines the pool, and records available thread masks by core. `NE_CREATE_VM` checks CPU availability, allocates enclave state and cpumasks, obtains an fd and anon file, asks the PCI device for a slot, initializes per-enclave state, links it into the PCI device enclave list, and returns slot UID plus fd. Enclave ioctls add vCPUs from the pool or explicit IDs, register 2 MiB-aligned hugetlb memory from the same NUMA node, merge physically contiguous chunks before `SLOT_ADD_MEM`, validate minimum memory/full cores/vCPU count, and start the enclave. Release stops a running enclave, frees the slot, returns CPUs, drops pinned pages, removes list entries, and frees state.

## Dependencies and Integration
Depends on `ne_do_request()` from `ne_pci_dev.c`, CPU hotplug, topology sibling masks, hugetlb pages, anon inodes, miscdevice, vsock CID ABI, Linux Nitro Enclaves UAPI, and shared global `ne_devs`.

## Risks and Test Signals
High-risk areas are CPU hotplug rollback, locking order between PCI enclave list and per-enclave mutex, page references after partial `SLOT_ADD_MEM` failure, ensuring all sibling CPUs are assigned before start, stale `has_event` poll semantics, and `ne_devs.ne_pci_dev` availability during ioctl/release. Existing KUnit only covers physical-region merge behavior. Additional tests should cover CPU-pool parsing and teardown, enclave create failure cleanup, memory overlap and NUMA rejection, vCPU auto/allocation, start validation, release after running and after partial setup, PCI command failures, and event wakeups from `ne_pci_dev.c`.
