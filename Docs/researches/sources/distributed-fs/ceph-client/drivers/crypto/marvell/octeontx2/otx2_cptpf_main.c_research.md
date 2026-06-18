# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_main.c

## Purpose
This is the PCI PF driver entry point for Marvell RVU CPT hardware. It probes PF devices, maps registers, initializes AF/PF mailbox, discovers engine resources, initializes LMTST support, creates sysfs/devlink surfaces, manages SR-IOV VF enablement, and handles VF mailbox/FLR/ME interrupt setup.

## Important APIs and functions
Driver entry points are `otx2_cptpf_probe()`, `otx2_cptpf_remove()`, and `otx2_cptpf_sriov_configure()`. SR-IOV helpers are `cptpf_sriov_enable()` and `cptpf_sriov_disable()`. Mailbox setup helpers include `cptpf_afpf_mbox_init()`, `cptpf_register_afpf_mbox_intr()`, `cptpf_vfpf_mbox_init()`, and `cptpf_register_vfpf_intr()`. FLR and ME paths use `cptpf_vf_flr_intr()`, `cptpf_flr_wq_handler()`, and `cptpf_vf_me_intr()`. Sysfs attributes are `kvf_limits` and `sso_pf_func_ovrd`.

## Control flow
Probe allocates `otx2_cptpf_dev`, enables PCI and DMA, requests BARs, maps PF registers, verifies AF readiness, allocates MSI-X vectors, sets hardware capability flags, initializes AF mailbox, sends ready, reads PF resources, initializes LMTST and engine group structures, creates sysfs group, and registers devlink. SR-IOV enable initializes VF/PF mailbox memory and workqueues, initializes FLR work, registers VF mailbox/FLR/ME interrupts, discovers engine capabilities, creates default engine groups, then calls `pci_enable_sriov()`. Disable reverses those resources and drops the module reference.

## State and persistence
PF state is all in memory: mailbox objects, workqueues, VF table, engine groups, LFs, capabilities, sysfs values, and devlink registration. `kvf_limits` and `sso_pf_func_ovrd` can be changed via sysfs while loaded but are not persisted across reload. Engine group creation persists for the lifetime of the PF and enabled VFs.

## Dependencies and integration points
This file depends on PCI core, RVU registers, mailbox helpers, microcode manager, LF common code, devlink support, and CN10K LMTST helpers. It provides the PF service layer that VFs depend on for capability discovery and engine-group selection.

## Risks and edge cases
Probe defers if AF is not initialized or ready-message times out. Error unwinds must destroy mailboxes/workqueues and remove sysfs/devlink in exact reverse order. SR-IOV enable does engine discovery and microcode setup before `pci_enable_sriov()`; failures must not leave interrupts enabled. FLR handling relies on per-VF ordered work and re-enables interrupts only after AF confirms reset. `kvf_limits` is bounded by online CPUs but can affect later VF LF count.

## Test signals
Signals include successful PF bind/unbind, probe defer when AF is unavailable, SR-IOV enable/disable with different VF counts including over 64, VF FLR recovery, sysfs validation, devlink registration, microcode group creation, and no leaked IRQ/workqueue resources under failure injection.
