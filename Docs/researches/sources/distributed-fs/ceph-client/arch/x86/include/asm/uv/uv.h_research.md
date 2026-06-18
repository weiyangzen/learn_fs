# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv.h

Purpose: top-level UV platform detection and initialization interface.

Important APIs/types/functions: `enum uv_system_type`, `UV_PROC_NODE`, `uv()`, `uv_systab_phys`, `get_uv_system_type()`, `is_early_uv_system()`, `is_uv_system()`, `is_uv_hubbed()`, `uv_cpu_init()`, `uv_nmi_init()`, and `uv_system_init()`.

Control flow: `CONFIG_X86_UV` builds expose real detection/init functions and early detection from a valid UV system table physical address. Non-UV builds inline to `UV_NONE`, false, or no-op.

State/persistence: UV detection state includes `uv_systab_phys` and runtime platform classification maintained by implementation files.

Dependencies/integration: depends on EFI when UV is enabled. Integrated with x86 platform setup, per-CPU UV initialization, NMI setup, and `/proc/sgi_uv` naming.

Risks/test signals: false UV detection can route normal x86 systems into UV-specific paths; missed detection disables UV platform support. Test UV and non-UV boots, early EFI systab detection, hubbed/hubless UV variants, CPU bring-up, and NMI initialization.
