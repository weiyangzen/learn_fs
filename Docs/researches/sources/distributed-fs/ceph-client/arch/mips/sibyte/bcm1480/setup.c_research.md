# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/setup.c

Purpose: BCM1480/BCM1x55 SoC identification and clock reporting. It decodes system revision registers and exports SoC revision metadata.

Important APIs and control flow: globals `sb1_pass`, `soc_pass`, `soc_type`, `periph_rev`, and `zbbus_mhz` capture CPU/SoC state. `setup_bcm1x80_bcm1x55()` maps revision values to pass strings and peripheral revision. `sys_rev_decode()` chooses SoC family/name from system revision and part type. `bcm1480_setup()` reads CP0 PRID, system revision, and PLL divisor, restarts on unknown chip, computes ZBbus frequency, and logs SoC/pass/board type.

State, persistence, and integration: exported SoC state informs drivers and diagnostics. Dependencies include SCD registers, CP0 PRID, reboot hook availability, and `get_system_type()`. Risks include forced restart on unknown parts, defaulting unknown revisions to periph rev 1, and fixed PLL formula. Test signals are "Broadcom SiByte ..." boot log, exported `soc_type`/`periph_rev`, and correct ZBbus MHz.
