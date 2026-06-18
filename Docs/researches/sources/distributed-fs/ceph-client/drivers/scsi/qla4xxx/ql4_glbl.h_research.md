<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h

Purpose: central cross-file interface for the qla4xxx driver. It declares the initialization, reset, mailbox, IOCB, interrupt, flash/NVRAM, DDB, CHAP, ACB, 8xxx hardware, BSG, sysfs, minidump, and module-parameter symbols shared across the qla4xxx implementation files.

Important APIs/types/functions: core entry points include `qla4xxx_initialize_adapter()`, `qla4xxx_start_firmware()`, `qla4xxx_init_rings()`, `qla4xxx_send_command_to_isp()`, `qla4xxx_mailbox_command()`, `qla4xxx_request_irqs()`, `qla4xxx_process_response_queue()`, and `qla4xxx_process_aen()`. Firmware/data management declarations include `qla4xxx_initialize_fw_cb()`, `qla4xxx_get_fwddb_entry()`, `qla4xxx_set_ddb_entry()`, `qla4xxx_get_default_ddb()`, `qla4xxx_set_param_ddbentry()`, `qla4xxx_get_chap_index()`, `qla4xxx_set_chap()`, `qla4xxx_get_flash()`, `qla4xxx_set_flash()`, `qla4xxx_get_nvram()`, and `qla4xxx_set_nvram()`. 82xx/83xx-specific declarations cover IDC locks, reset handlers, register accessors, MSI/MSI-X handlers, firmware bootstrap, port config, and minidumps.

Control flow: the header is declarative, but it shows the subsystem boundaries. Probe/reset paths call PCI setup, firmware start, firmware control-block init, sys-info reads, interrupt setup, and DDB rebuild. SCSI queuecommand paths call IOCB builders. Error handlers call abort/LUN reset/target reset mailbox commands. Interrupt handlers call response queue and mailbox/AEN decoders, which in turn set DPC work bits.

State and persistence: external parameters such as `ql4xextended_error_logging`, `ql4xdontresethba`, `ql4xenablemsix`, `ql4xmdcapmask`, and `ql4xenablemd` influence debug logging, reset decisions, interrupt mode, and minidump capture. Persistent state is managed through declared flash, NVRAM, CHAP, DDB, and ACB helpers.

Dependencies and integration: integrates internal qla4xxx files with the SCSI midlayer, libiscsi, PCI/MSI, BSG, sysfs attribute groups, firmware dump support, DMA pools, and adapter-specific operation tables. The many 8xxx declarations show that one driver binary supports legacy 40xx plus 82xx/83xx/84xx families through `isp_ops`.

Risks and test signals: duplicate prototypes for `qla4xxx_intr_handler()`, `qla4xxx_disable_acb()`, `qla4xxx_set_acb()`, and `qla4xxx_get_acb()` are benign but show interface sprawl. Prototype drift here causes compile failures across many files; behavioral drift causes reset/login/interrupt regressions. Test signals include allmodconfig-style builds, 40xx vs 82xx/83xx hardware paths, MSI/MSI-X fallback, CHAP/DDB user flows, BSG vendor commands, and AER/removal failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h -->
