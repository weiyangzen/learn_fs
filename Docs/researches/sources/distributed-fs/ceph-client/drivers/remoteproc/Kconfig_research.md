<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/Kconfig

Purpose: Defines build-time configuration for the Linux remoteproc framework and platform-specific remote processor drivers.

Important APIs and types: The top-level `REMOTEPROC` bool selects common dependencies such as CRC32, firmware loader, virtio, and device coredump support. Sub-options include the character-device interface, i.MX, Ingenic, Mediatek SCP, OMAP, Wakeup M3, DA8xx, Keystone, Meson AO ARC, PRU, Qualcomm Q6/WCNSS/sysmon, R-Car, ST, STM32, TI K3 DSP/M4/R5, and Xilinx R5 drivers.

Control flow: The menu gates all platform drivers under `if REMOTEPROC`. Each `config` entry declares architecture, subsystem, mailbox, firmware, rpmsg, syscon, TrustZone, or compile-test dependencies. `select` statements pull in shared helper libraries such as QCOM common code, MDT loader, PIL info, or mailbox support.

State and persistence: Kconfig state persists in the kernel build configuration. It controls which objects are built in, built as modules, or omitted.

Dependencies and integration points: Integrates with architecture Kconfig symbols, remoteproc core, rpmsg transports, mailbox subsystems, Qualcomm SCM/sysmon, TI SCI, and platform-specific SoC support.

Risks: `select` can force helper code without surfacing all runtime platform requirements. Architecture-only dependencies limit compile coverage for some drivers. DA8xx requires `DMA_CMA`, and many Qualcomm options require optional rpmsg providers to be disabled or enabled compatibly.

Test signals: `allyesconfig`, `allmodconfig`, architecture-specific defconfigs, COMPILE_TEST where supported, dependency resolution for Qualcomm and TI K3 stacks, and module/builtin combinations with `REMOTEPROC_CDEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/Kconfig -->
