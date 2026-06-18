# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Kconfig

Purpose: declares build options for low-level PCMCIA SCSI adapter support.

Important APIs/options: `SCSI_LOWLEVEL_PCMCIA` gates the menu on SCSI and PCMCIA. The submenu additionally requires module builds (`SCSI && PCMCIA && m`). Driver symbols are `PCMCIA_AHA152X`, `PCMCIA_FDOMAIN`, `PCMCIA_NINJA_SCSI`, `PCMCIA_QLOGIC`, and `PCMCIA_SYM53C500`; several depend on `HAS_IOPORT`, AHA152X selects `SCSI_SPI_ATTRS`, and Future Domain selects `SCSI_FDOMAIN`.

Control flow/state: controls which modules the Makefile emits. `PCMCIA_NINJA_SCSI` blocks normal 64-bit builds unless `COMPILE_TEST` is active.

Dependencies/integration: paired with `drivers/scsi/pcmcia/Makefile`; help text documents supported cards and module names.

Risks/test signals: wrong dependencies can expose old I/O code on unsupported architectures. Test with allmodconfig/COMPILE_TEST module builds and expected module names.
