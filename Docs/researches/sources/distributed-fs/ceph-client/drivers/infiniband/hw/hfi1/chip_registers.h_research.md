# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip_registers.h

Purpose: generated-style register map for HFI1 silicon. It names the base address blocks (`CORE`, `ASIC`, `MISC`, `DCC_CSRS`, `DC_LCB_CSRS`, `DC_8051_CSRS`, `RXE`, `TXE`, `CCE`, PCIe) and defines offsets, reset values, masks, shifts, and status bits for link, firmware, receive, send, DMA, interrupt, GPIO, QSFP, EEPROM, thermal, PCIe, and error reporting registers.

Important APIs/types: this header exports macros only. Important families include `DCC_CFG_*` link/port configuration, `DC_DC8051_*` firmware command/status/RAM access, `DC_LCB_*` link-control-block status and error bits, `ASIC_*` SBUS/GPIO/QSFP/EEPROM/thermal registers, `CCE_*` interrupt/MSI-X/error registers, `RCV_*` context/TID/header/eager/QP-map registers, and `SEND_*` PIO, SDMA, egress, credit, SC/VL, and error registers.

Control flow: no executable control flow is present. Driver code composes these offsets with `read_csr()`, `write_csr()`, `read_kctxt_csr()`, `write_kctxt_csr()`, `read_uctxt_csr()`, and per-engine/per-context strides defined in `chip.h`.

State and persistence: every macro corresponds to persistent device state or W1C/W1S status in MMIO, PCI config space, or firmware-facing register windows. Hardware state includes interrupt routing, receive queue heads/tails, TID tables, send contexts, SDMA descriptors, credit accounting, port link state, 8051 requests, QSFP GPIO state, EEPROM controller mode, and accumulated counters.

Dependencies and integration: consumed by `chip.h` and all low-level HFI1 implementation files. It is the single source for field masks used by chip init, firmware loading, IRQ setup, debugfs CSR windows, EPROM access, link-state changes, receive queue management, and send/SDMA programming.

Risks: macro mistakes are high blast radius: a wrong mask or offset can acknowledge the wrong interrupt, clear error state, expose user contexts, or program packet routing incorrectly. Because many values are raw constants rather than typed fields, misuse is usually detected only by hardware behavior. W1C and reset-value semantics must be preserved when callers modify bitfields.

Test signals: compile coverage is necessary but insufficient. Useful signals are probe register traces, MSI-X mapping checks, link bringup, receive/send loopback, SDMA stress, error injection with expected status bits, EPROM/QSFP diagnostics, and comparison against hardware specification or generated-register provenance.
