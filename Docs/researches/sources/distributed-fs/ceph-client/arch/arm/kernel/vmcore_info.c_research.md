# sources/distributed-fs/ceph-client/arch/arm/kernel/vmcore_info.c

Purpose: contributes ARM-specific metadata to crash dump vmcore notes. `arch_crash_save_vmcoreinfo` records `CONFIG_ARM_LPAE` when LPAE is enabled.

Control flow is invoked by the crash dump infrastructure during vmcoreinfo collection. There is no local state; the function conditionally emits configuration metadata through `VMCOREINFO_CONFIG`. Dependencies are `linux/vmcore_info.h` and the crash/kdump vmcoreinfo pipeline. The main risk is missing architecture flags that crash tools need to decode page tables. Test signals are kdump vmcoreinfo contents on LPAE and non-LPAE kernels.
