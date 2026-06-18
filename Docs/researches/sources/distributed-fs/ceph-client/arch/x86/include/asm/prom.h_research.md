<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h

Purpose: provides x86 OpenFirmware/device-tree declarations. Important APIs are `of_ioapic`, `initial_dtb`, `add_dtb()`, `x86_of_pci_init()`, `x86_flattree_get_config()`, and the exported boot `cmd_line`.

Control flow: when `CONFIG_OF` is enabled, early boot and PCI initialization can record a DTB address, parse the flattened tree, and initialize PCI/device-tree resources. Without OF support, the header supplies no-op stubs and `of_ioapic` as zero so call sites compile away.

State and persistence: stores only boot-time DTB and command-line state; nothing persists beyond kernel runtime. Dependencies include Linux OF, PCI, IRQ, and x86 setup definitions. Risks are wrong conditional stubs masking missing OF initialization or breaking early boot command-line/DTB parsing. Test signals include OF-enabled x86 boot with IOAPIC and PCI nodes, no-OF builds, and DTB command-line propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h -->
