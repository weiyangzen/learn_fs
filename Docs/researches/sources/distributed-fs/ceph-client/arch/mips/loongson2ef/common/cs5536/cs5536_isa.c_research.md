# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_isa.c

Purpose: virtualizes PCI configuration space and local BARs for the CS5536 ISA bridge.

Important APIs/functions: `pci_isa_write_bar`, `pci_isa_read_bar`, `pci_isa_write_reg`, `pci_isa_read_reg`, and `cs5536_isa_mmio_always_on`.

Control flow: BAR helpers handle sizing via soft flags or program DIVIL LBARs and SB RCONF mappings. PCI command IO enable toggles DIVIL LBAR enablement. Status writes clear selected SB error flags. UART interrupt pseudo-registers program PIC route selectors. Reads synthesize standard bridge config fields, BARs, error-derived status, class revision, and interrupt-line values. A PCI fixup marks ISA MMIO always-on to protect early MFGPT timer interrupts.

State and persistence: static arrays map BAR indexes to MSR registers, soft flags, ranges, and lengths; hardware MSRs persist BAR/error/interrupt routing state.

Dependencies and integration: part of CS5536 VSM; depends on PCI fixup framework and MSR helpers. Supports SMB, GPIO, MFGPT, IRQ, PMS, and ACPI local bars.

Risks: BAR index validity is assumed by callers. The MMIO-always-on fixup prevents timer hangs during PCI config races and must not be removed without replacing that guarantee.

Test signals: ISA bridge PCI enumeration, BAR sizing/programming, UART interrupt routing, error status clear tests, and MFGPT timer operation during PCI probing.
