# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.c

Purpose: implements Broadcom mobile, NSP, and BCM2836 SMP startup methods.

Important APIs/types/functions: `scu_a9_enable()`, `secondary_boot_addr_for()`, `kona_boot_secondary()`, `bcm23550_boot_secondary()`, `nsp_write_lut()`, `nsp_boot_secondary()`, `bcm2836_boot_secondary()`, and SMP operation tables for Kona, BCM23550, NSP, and BCM2836.

Control flow: Cortex-A9 platforms optionally enable SCU in prepare. Kona reads each CPU node's `secondary-boot-reg`, writes the physical `secondary_startup` address ORed with CPU ID, sends `sev`, and waits for ROM to clear the low bits. BCM23550 layers a CDC run-state command on top. NSP writes the startup address into SKU-ROM LUT and sends a wakeup IPI. BCM2836 writes `secondary_startup` to the local interrupt controller mailbox and sends `sev`.

State and persistence: no durable software state beyond CPU-present changes if SCU setup fails; boot registers/mailboxes/LUTs retain the last startup address.

Dependencies and integration: depends on CPU DT properties and compatible CPU methods, ARM SCU helpers, Broadcom local interrupt controller registers, and `secondary_startup`.

Risks: boot-register address or CPU ID mismatch strands secondaries. The Kona wait is short and local-clock based; slow firmware handoff can appear as timeout. BCM2836 mailbox offsets are register-layout sensitive.

Test signals: CPU online count across Broadcom mobile/NSP/Raspberry Pi compatible DTs, bad/missing `secondary-boot-reg` negative tests, and secondary boot timeout logs.
