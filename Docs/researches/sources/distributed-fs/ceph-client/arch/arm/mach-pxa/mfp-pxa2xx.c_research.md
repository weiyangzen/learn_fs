<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c

Purpose: runtime MFP/pinmux configuration and low-power GPIO handling for PXA25x/PXA27x.

Important APIs/functions: `pxa2xx_mfp_config()` applies arrays of encoded pin configs; `pxa2xx_mfp_set_lpm()` changes only low-power state; `gpio_set_wake()` programs GPIO/keypad wake routing; `keypad_set_wake()` handles PXA27x keypad matrix wake bits. `pxa2xx_mfp_syscore` saves and restores GAFR, GPDR, GPLR, and PGSR across suspend.

Control flow: postcore init validates CPU family, initializes valid/wakeup GPIO descriptors, clears PSSR RDH, and seeds low-power GPDR state. Configuration writes alternate function registers, direction, low-power output states, and wake validation under local IRQ disable. Suspend copies keep-output states into PGSR, drives sleep levels, and updates directions; resume restores saved run registers.

State and persistence: static `gpio_desc[]` records per-pin validity, wake masks, mux masks, direction inversion, and last config. `gpdr_lpm[]` and saved register arrays preserve low-power and suspend state.

Dependencies and integration: used by legacy board files and PXA27x AC97 workaround. Depends on GPIO helpers, CPU detection, PXA2xx power/gpio registers, and syscore PM.

Risks and test signals: wake mux conflicts return `-EBUSY`; invalid pins warn and skip. Keep-output logic can affect power rails. Test pin config on PXA25x/PXA27x boards, GPIO wake from suspend, keypad wake, and resume restoration of GAFR/GPDR/GPLR/PGSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c -->
