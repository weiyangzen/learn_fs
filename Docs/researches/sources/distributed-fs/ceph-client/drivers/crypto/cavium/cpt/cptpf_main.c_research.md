# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_main.c

Purpose: implements the Thunder CPT physical-function PCI driver, including reset, BIST checks, microcode loading, core-group programming, PF interrupts, SR-IOV enablement, and remove/shutdown cleanup.

Important APIs and control flow: `cpt_probe()` enables PCI, maps BAR0, sets a 48-bit DMA mask, initializes hardware through `cpt_device_init()`, registers mailbox MSI-X, loads `cpt8x-mc-ae.out` and `cpt8x-mc-se.out`, and enables SR-IOV. `cpt_ucode_load_fw()` requests firmware, allocates coherent DMA, byte-swaps microcode, and calls `do_cpt_init()`. `do_cpt_init()` disables interrupts, assigns a microcode group, programs `ENGX_UCODE_BASE`, group masks, and core enables, then marks the PF ready. Remove disables cores, unloads microcode, unregisters interrupts, disables SR-IOV, and releases PCI resources.

State and persistence: state is `struct cpt_device`, hardware reset state, loaded coherent firmware buffers, engine group masks, and SR-IOV VF enablement. Hardware firmware and core enables persist until removed or reset.

Dependencies and integration points: depends on Linux PCI, firmware loader, MSI-X, DMA coherent allocation, `cptpf_mbox.c`, and CPT CSR/bitfield headers. VFs cannot initialize until firmware groups and PF mailboxes are ready.

Risks and test signals: risks include `GENMASK(num_cores, 0)` enabling one more bit than a count-style name suggests, duplicated/unbraced `cpt->num_vf_en = total_vf_cnt`, error paths after VF software init not always cleaning VF queues, and firmware byte-swap assumptions. Test signals include BIST pass, firmware load messages, PF mailbox IRQ delivery, SR-IOV VFs appearing, VF group binding, and remove freeing all coherent microcode buffers.
