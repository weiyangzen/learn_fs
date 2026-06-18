# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/pci.c

Purpose: generic TXX9 PCI resource allocation, bridge quirks, IRQ mapping hook, and boot-option parser.

Important APIs/types/functions: `txx9_pci66_check`, `txx9_alloc_pci_controller`, `txx9_pcibios_setup`, `pcibios_map_irq`, SLC90E66 and TC35815 fixups, BIST final fixup.

Control flow and state: allocates PCI MEM/MMIO/IO windows, sets MIPS I/O base, registers arch init, probes 66MHz capability, configures ISA bridge cascade/Super I/O when enabled, applies device fixups, and parses `pci=` options such as `picmg`, `clk=`, and `err=`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: resource allocation can fail depending on physical map; global IRQ map callback must be initialized; final BIST on every device may expose slow/broken hardware; bridge quirks are device-ID specific.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
