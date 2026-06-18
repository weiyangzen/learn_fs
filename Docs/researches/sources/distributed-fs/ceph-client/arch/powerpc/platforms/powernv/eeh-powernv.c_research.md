
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/eeh-powernv.c

Purpose: implements PowerNV-specific EEH operations for PCI error detection, isolation, diagnostics, reset, config-space mediation, error injection, and OPAL event handling.

Important APIs/types/functions: registers `pnv_eeh_ops` through `eeh_init()`. Key functions include `pnv_eeh_probe()`, `pnv_eeh_post_init()`, `pnv_eeh_set_option()`, `pnv_eeh_get_state()`, `pnv_eeh_reset()`, `pnv_eeh_next_error()`, `pnv_eeh_read_config()`, `pnv_eeh_write_config()`, `pnv_eeh_restore_config()`, and exported reset helper `pnv_pci_reset_secondary_bus()`. Debugfs includes error injection and raw PHB register accessors when enabled.

Control flow: init verifies OPAL firmware, sets EEH probe mode, sizes PE aux diagnostic buffers, hooks `ppc_md.pcibios_bus_add_device`, and registers the backend. Post-init requests the OPAL PCI error event IRQ, creates debugfs files per PHB, and toggles PHB EEH flags. Device probe records PCI capabilities, builds PE trees, caches primary buses, saves BARs, and enables global EEH on first device. OPAL event IRQ disables itself and queues EEH core recovery. `pnv_eeh_next_error()` drains pending events, walks PHBs, asks OPAL for next errors, classifies IOC/PHB/PE conditions, freezes compound PEs, dumps diagnostics, and unmasks the IRQ when no actionable error remains.

State and persistence: persistent kernel state includes `eeh_event_irq`, PE trees, PE state flags such as isolated/config-blocked/reset, PHB flags, saved BARs, diagnostic buffers, and debugfs files. It does not write disk state.

Dependencies and integration points: integrates with OPAL PCI calls, PowerNV PHB/IODA structures, generic EEH core, PCI config accessors, MSI/IRQ domain code, debugfs, firmware feature flags, and PCI bus/device add hooks.

Risks: recovery sequencing is sensitive: frozen state is intentionally kept until BAR restore, config access may be blocked for problematic adapters, and parent PE migration affects which device gets recovered. Debugfs error injection can deliberately fault hardware. OPAL return-code mapping must not hide fatal PHB/IOC states. IRQ masking/unmasking prevents event storms but can lose progress if `next_error` is not called.

Test signals: EEH injection via debugfs, OPAL PCI error events, frozen PE recovery, PHB reset/fenced PHB recovery, VF FLR/AF FLR, Broadcom restricted-config behavior, diagnostic log dumps, and PCI config access behavior while isolated.
