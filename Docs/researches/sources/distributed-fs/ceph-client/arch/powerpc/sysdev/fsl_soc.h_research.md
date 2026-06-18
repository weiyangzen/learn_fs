<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h

Purpose: Declares the public Freescale SoC helper interface shared by PowerPC platform code and drivers.

Important APIs/types/functions: Declares `get_immrbase()`, `fsl_get_sys_freq()`, conditional `get_brgfreq()`/`get_baudrate()` stubs, `enum fsl_diu_monitor_port`, `struct platform_diu_data_ops`, exported `diu_ops`, and hypervisor hooks `fsl_hv_restart()`/`fsl_hv_halt()`.

Control flow: The header has no runtime control flow. Its only logic is compile-time selection of real CPM/QE clock declarations versus inline stubs that return `-1`.

State and persistence: Defines no storage except the external `diu_ops` declaration. The callback struct describes persistent board-provided DIU operations for pixel format, gamma, monitor routing, pixel clock, validation, and bootmem release.

Dependencies and integration points: Includes `asm/mmu.h` and forwards SPI/device-node types. Used by Freescale platform setup, DIU framebuffer/platform code, CPM/QE users, and ePAPR hypervisor machine descriptors.

Risks: The inline fallback uses `u32` return type with `-1`, preserving a sentinel but inviting accidental use as a valid high clock frequency. DIU callbacks are optional global function pointers, so callers must check availability.

Test signals: Build coverage with and without `CONFIG_CPM`, `CONFIG_QUICC_ENGINE`, `CONFIG_FB_FSL_DIU`, and `CONFIG_EPAPR_PARAVIRT`; consumers should handle `-1` helper returns.

Source read size: 48 lines, 1265 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h -->
