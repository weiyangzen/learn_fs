
# sources/distributed-fs/ceph-client/arch/x86/include/asm/espfix.h

Purpose: ESPFIX64 per-CPU stack declarations and initialization hooks.

Important APIs and control flow: under `CONFIG_X86_ESPFIX64`, declares read-mostly per-CPU `espfix_stack` and `espfix_waddr`, plus `init_espfix_bsp()` and `init_espfix_ap()`. Without ESPFIX64, AP init is a no-op stub.

State, dependencies, and risks: state is per-CPU ESPFIX mapping/stack addresses used to handle 16-bit stack segment return quirks. Dependencies include per-CPU setup, CPU bringup, and entry/IRET paths. Risks include missing AP initialization and regressions in legacy 16-bit compat returns. Test signals are espfix-specific tests, 16-bit return/IRET coverage, and CPU hotplug.
