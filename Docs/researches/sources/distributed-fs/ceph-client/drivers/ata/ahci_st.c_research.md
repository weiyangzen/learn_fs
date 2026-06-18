# sources/distributed-fs/ceph-client/drivers/ata/ahci_st.c

Purpose: STMicroelectronics AHCI platform driver handling ST power/reset controls and OOB timing setup.

Important APIs/types: `struct st_ahci_drv_data`, `st_ahci_configure_oob`, `st_ahci_deassert_resets`, `st_ahci_probe_resets`, `st_ahci_host_stop`, `st_ahci_probe`, `st_ahci_suspend`, `st_ahci_resume`.

Control flow: probe allocates private reset data, gets resources, obtains optional resets, deasserts them, enables resources, writes OOB timing with write-enable sequence, and activates. Suspend suspends host, asserts power-down reset, and disables resources; resume reverses and reprograms OOB timing.

State/persistence: reset handles, reset line state, OOB timing register values, and resource state.

Dependencies/integration: OF compatible `st,ahci`, reset framework, `ahci_platform`, libata host stop and PM, MMIO OOB registers.

Risks/test signals: optional resets make board behavior variable; OOB timing must be restored after PM. Test reset logs, link negotiation, suspend/resume, and host-stop cleanup.
