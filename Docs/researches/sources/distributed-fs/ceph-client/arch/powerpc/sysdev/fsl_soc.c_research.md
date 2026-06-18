<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c

Purpose: Provides common Freescale SoC helpers for IMMR base discovery, system/BRG/baud clock lookup, reset-control based restart, DIU data callbacks, and ePAPR hypervisor restart/halt hooks.

Important APIs/types/functions: Exports `get_immrbase()`, `fsl_get_sys_freq()`, `get_brgfreq()`, `get_baudrate()`, and optional `diu_ops`. Internal restart support uses `setup_rstcr()` and `fsl_rstcr_restart()`. Paravirtual control is through `fsl_hv_restart()` and `fsl_hv_halt()`.

Control flow: Clock/base helpers lazily search OF nodes, cache the discovered value in static variables initialized to `-1`, and return `-1` if no usable node/property exists. `setup_rstcr()` scans `global-utilities` nodes for `fsl,has-rstcr`, maps the reset control register at offset `0xb0`, and registers a high-priority restart notifier. The restart notifier disables local IRQs and writes HRESET_REQ. Hypervisor restart/halt issue Freescale hcalls and spin forever.

State and persistence: Persistent state is cached `immrbase`, cached static clock rates in helper functions, mapped `rstcr`, exported DIU callback table, and machine restart/halt integration through notifier or platform hooks.

Dependencies and integration points: Uses OF node/property APIs, PowerPC `ppc_md`/restart infrastructure, CPM/QUICC Engine clock users, Freescale DIU framebuffer users, and Freescale hypervisor hcall wrappers.

Risks: Cached `-1` values make missing properties sticky. `setup_rstcr()` uses `of_iomap(np, 0) + 0xb0` and tests the adjusted pointer rather than the original mapping, so a failed mapping plus offset arithmetic is subtle. Clock helpers return unsigned `u32` values using `-1` as sentinel, requiring callers to know that convention.

Test signals: Boot on FSL BookE/86xx boards with valid and missing `soc` clocks, CPM/QE serial clock users, restart through RSTCR, DIU platform data consumers, and ePAPR paravirtual restart/halt paths.

Source read size: 217 lines, 4524 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c -->
