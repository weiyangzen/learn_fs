# sources/distributed-fs/ceph-client/drivers/pci/proc.c

## Purpose
This file implements the legacy `/proc/bus/pci` interface. It exposes per-device config-space files, optional BAR mmap support, and the `/proc/bus/pci/devices` summary used by older userspace tooling.

## Important APIs, types, and functions
`proc_bus_pci_read()` and `proc_bus_pci_write()` perform aligned config-space reads and writes from userspace buffers. `proc_bus_pci_ioctl()` handles controller-domain selection and mmap mode controls. Under `HAVE_PCI_MMAP`, `struct pci_filp_private`, `proc_bus_pci_open()`, `proc_bus_pci_release()`, and `proc_bus_pci_mmap()` track whether userspace requested IO or memory BAR mapping and optional write combining. The seq-file path uses `pci_seq_start()`, `pci_seq_next()`, `pci_seq_stop()`, and `show_device()`. Device/bus attachment entry points are `pci_proc_attach_device()`, `pci_proc_detach_device()`, and `pci_proc_detach_bus()`.

## Control flow
`pci_proc_init()` creates `/proc/bus/pci`, creates the `devices` seq file, marks proc support initialized, and attaches proc entries for already-known devices. Later enumeration calls `pci_proc_attach_device()` to create bus directories and per-device files named by slot/function. Reads clamp non-admin users to standard config space, take a runtime-PM config reference, perform byte/word/dword reads with little-endian conversion, and update the file position. Writes require lockdown permission checks, similarly chunk user data into config writes, and update inode size.

## State and persistence
The file maintains `proc_initialized`, the top-level `proc_bus_pci_dir`, each `pci_bus::procdir`, and each `pci_dev::procent`. Optional mmap state is per-open-file private memory. There is no durable storage, but userspace writes can persist by modifying device PCI config registers until reset or driver changes.

## Dependencies and integration points
It depends on procfs, seq_file, Linux capabilities, lockdown LSM checks, PCI config access wrappers, runtime PM config helpers, architecture mmap support, `pci_resource_to_user()`, `pci_mmap_fits()`, `pci_mmap_resource_range()`, and global PCI device iteration. It integrates with PCI enumeration/removal when devices and buses are attached or detached.

## Risks
This interface intentionally exposes low-level config access. Writes and mmap are gated by lockdown and capabilities, but incorrect config writes can destabilize hardware. The read path allows non-admin access only to conventional header space because some hardware locks up on undefined config reads. Mmap depends on accurate resource bounds and exclusivity checks; write-combining is only allowed for prefetchable memory BARs. Error handling ignores individual `__get_user()`/`__put_user()` failures after `access_ok()`, matching legacy style but worth preserving cautiously.

## Test signals
Check that `/proc/bus/pci/devices` lists expected domain/bus/devfn IDs, resources, IRQs, and driver names. Per-device files should expose 64 or 128 bytes to unprivileged readers and full `cfg_size` to `CAP_SYS_ADMIN`. Lockdown mode should reject writes/ioctls/mmap. Mmap tests should cover IO versus MEM mode, non-mappable BARs, exclusive iomem, prefetch-only write combining, and detach cleanup removing proc entries.
