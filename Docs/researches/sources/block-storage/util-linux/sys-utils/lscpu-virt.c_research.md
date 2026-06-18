# File Research: sources/block-storage/util-linux/sys-utils/lscpu-virt.c

`lscpu-virt.c` detects virtualization features, hypervisor vendor, and virtualization type for `lscpu`.

Key behavior:
- Reads arbitrary memory chunks from files through `get_mem_chunk()`, shared with DMI parsing.
- Detects hypervisors from SMBIOS/DMI data in sysfs or `/dev/mem`.
- Detects common virtual PCI devices for Xen, VMware, and VirtualBox.
- On x86, reads CPUID hypervisor leaf `0x40000000`.
- On x86, optionally probes VMware’s backdoor I/O port under a temporary SIGSEGV handler, only as root.
- Detects WSL first via `/proc/sys/kernel/osrelease`.
- Handles Xen features to distinguish full virtualization from paravirtual/PVH cases.
- Handles PowerPC virtualization through device-tree compatibility and partition metadata.
- Handles s390 PR/SM and KVM from `/proc/sysinfo`.
- Detects OpenVZ/Virtuozzo, User-mode Linux, and Linux-VServer container/paravirtual cases.
- Exposes `lscpu_read_virtualization()` and `lscpu_free_virtualization()`.

Important dependencies:
- DMI parser from `lscpu-dmi.c`.
- `/proc`, `/sys`, `/dev/mem`, CPUID, device-tree, and optional low-level I/O support.
- Shared virtualization enums in `lscpu.h`.

Risk notes:
- `/dev/mem` DMI probing may fail for permission or kernel lockdown reasons and is treated as optional.
- VMware backdoor probing is fragile and intentionally guarded by root and SIGSEGV handling.
- Detection order matters; WSL is checked before VMware probing due to known crash risk.
