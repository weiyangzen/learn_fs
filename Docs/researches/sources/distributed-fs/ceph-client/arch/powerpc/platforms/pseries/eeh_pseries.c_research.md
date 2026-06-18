# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/eeh_pseries.c

Purpose: Implements pseries platform operations for Enhanced Error Handling of PCI devices and PEs using RTAS. It discovers PE config addresses, enables EEH, queries/reset PEs, retrieves error logs, configures bridges, supports SR-IOV allow-unfreeze, and registers pseries EEH ops.

Important APIs/types/functions: Maintains RTAS tokens for EEH functions, `slot_errbuf`, `slot_errbuf_lock`, and `eeh_error_buf_size`. Key functions include `pseries_pcibios_bus_add_device()`, `pseries_eeh_get_pe_config_addr()`, `pseries_eeh_phb_reset()`, `pseries_eeh_phb_configure_bridge()`, PCI capability scanners, `pseries_eeh_init_edev()`, `pseries_eeh_probe()`, exported `pseries_eeh_init_edev_recursive()`, EEH ops callbacks, SR-IOV allow-unfreeze helpers, and `eeh_pseries_init()`.

Control flow: Init resolves required RTAS tokens, selects `ibm,configure-pe` or `ibm,configure-bridge`, sets EEH flags, optionally resets PHBs for kdump/reset, and calls `eeh_init()`. Device add initializes the `eeh_dev`, discovers PE address via `ibm,get-config-addr-info*`, enables EEH using `ibm,set-eeh-option`, inserts the device into the PE tree, and saves BARs. Runtime EEH core callbacks issue RTAS state, reset, log, bridge configure, and config-space operations.

State and persistence: Persistent state includes RTAS token ids, EEH flags, PE tree relationships, per-device capability offsets/mode bits, PE config addresses, saved BAR state, SR-IOV last allow-unfreeze return codes, and the static RTAS-accessible error buffer.

Dependencies and integration points: Integrates with PCI device nodes, `pci_dn`, EEH core, RTAS PCI config access, pseries PCI hotplug, crashdump/reset flows, SR-IOV, proc/log error handling, and `ppc_md.pcibios_bus_add_device`.

Risks: PE address discovery differs across firmware revisions. Error-log buffer access uses a global spinlock because RTAS writes to a shared buffer. Reset/configure delays must match firmware semantics. VF PE insertion is manually adjusted after initial tree placement. Missing RTAS token support disables all EEH.

Test signals: PCI EEH probe logs, injected MMIO errors, PE freeze/thaw/reset recovery, bridge reconfiguration, RTAS error-log capture, SR-IOV VF recovery and allow-unfreeze, kdump/reset PHB reset path, and PCI hotplug/DLPAR device add are key.

Source read size: 926 lines, 25323 bytes.
