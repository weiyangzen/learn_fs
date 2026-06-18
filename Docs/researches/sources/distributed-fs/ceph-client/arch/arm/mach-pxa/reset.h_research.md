<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h

Purpose: reset-status constants and reset helper declarations for PXA.

Important definitions/APIs: reset status bits for hardware, watchdog, low-power exit, GPIO reset, and all reset bits. Declares `clear_reset_status()`, `pxa_register_wdt()`, and `init_gpio_reset()`.

Control flow and integration: SoC and reset code use these constants to pass reset causes into watchdog platform data and clear hardware status before reboot.

State and persistence: no state directly; constants map to hardware RCSR/ARSR bits.

Dependencies: no external include requirements beyond C type basics.

Risks and test signals: bit mapping must remain 1:1 with both PXA2xx RCSR and PXA3xx ARSR expectations. Test reset-cause reporting after hardware, watchdog, sleep-exit, and GPIO resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h -->
