# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/prom.c

Purpose: detects Falcon SoC identity and installs NMI/EJTAG exception vector setup hooks.

Important APIs/functions: `ltq_soc_detect`, `ltq_soc_nmi_setup`, and `ltq_soc_ejtag_setup`. It decodes chip ID/config/type registers into part number, revision, subrevision, name, type, compatible string, and revision text.

Control flow: reads `FALCON_CHIPID`, `FALCON_CHIPCONF`, and `FALCON_CHIPTYPE`; maps Falcon subtype values to Falcon-D/V/M/default names; assigns board-level NMI and EJTAG setup callbacks that write handler addresses into boot-vector registers.

State and persistence: fills caller-owned `struct ltq_soc_info`; writes boot exception-vector MMIO registers.

Dependencies and integration: called by generic Lantiq `prom_init()` and depends on `lantiq_soc.h` register definitions plus MIPS trap handler symbols.

Risks: unknown part numbers call `unreachable()`. Incorrect vector writes can break debug/NMI handling.

Test signals: boot log SoC string, Falcon variant detection, NMI/EJTAG handler entry tests, and DT compatibility matching.
