# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hdr.h

Purpose: Provides the low-level NetXen hardware register map, CRB address mapping constants, PCI window constants, flash/ROMUSB instruction registers, NIU MAC/PHY registers, link-status helpers, firmware state registers, semaphore offsets, interrupt vector definitions, and legacy interrupt configuration structures.

Important APIs and definitions: Defines `netxen_crbword_t`, hub/agent IDs, CRB hub address macros, PCI CRB window mapping, NIU GB/XG/AP register address macros, MIU/SIU test-agent offsets, link-state and P3 speed macros, firmware version/capability registers, CDRP command registers, WOL and port-mode registers, DIMM capability decoders, device-state values, firmware error decoders, PCI semaphore offsets, and `NX_LEGACY_INTR_CONFIG`.

Control flow: This header has no executable control flow; other files use its constants to compute MMIO/CRB addresses and decode hardware register values. It is foundational for context setup, ethtool register reads, link tests, pause control, flash access, firmware command submission, and interrupt setup.

State and persistence behavior: Names hardware and firmware state locations rather than storing state. Registers named here can represent persistent flash data, live firmware status, interrupt state, port mode, WOL config, and device reset/error state.

Dependencies and integration points: Included by `netxen_nic.h` and hardware access code. It bridges driver code to NetXen ASIC register layout and PCI memory-window rules.

Risks: Constants are hardware ABI; an incorrect address can corrupt device state or read misleading diagnostics. Many macros compose addresses through large window offsets, so 32-bit/64-bit address assumptions and PCI function indexing are important. Legacy interrupt table values must match hardware function routing.

Test signals: Hardware smoke tests for register access, link-state decode, pause register writes, CDRP firmware commands, flash/ROM reads, interrupt delivery for all PCI functions, WOL configuration, and ethtool register dump consistency. Static review should verify address macros used by source files point into intended CRB windows.
