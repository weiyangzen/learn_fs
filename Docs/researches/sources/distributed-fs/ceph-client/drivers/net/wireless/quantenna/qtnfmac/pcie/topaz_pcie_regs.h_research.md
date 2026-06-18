# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_regs.h

Purpose: defines Topaz PCIe DMA interrupt, LHost IPC/M2L interrupt, and legacy INTx register offsets and bit numbers.

Important APIs/types/functions: macros compute MMIO addresses for DMA write/read interrupt status/mask/clear/error and MSI write-address registers, LHost IPC4 interrupt/mask, LHost M2L interrupt/mask, PCIe config offset for legacy INTx, and interrupt word construction. IRQ numbers identify TX done, endpoint reset, TX stop, RX done, power-management endpoint interrupt, and control IPC interrupt.

Control flow: `topaz_pcie.c` uses these definitions to mask/unmask RX MSI delivery, signal endpoint TX/RX/control/reset/PM events, detect/deassert legacy INTx, and reset the endpoint.

State and persistence: no host state; all definitions target volatile MMIO registers.

Dependencies and integration points: consumed by Topaz PCIe transport. It must match Topaz hardware register layout and the firmware interrupt protocol.

Risks: wrong offsets or IRQ bit numbers break firmware handshakes, TX/RX completion, reset, or PM signaling. RX interrupt masking depends on the DMA write-done MSI address registers, so these offsets are especially sensitive.

Test signals: Topaz MSI RX interrupt enable/disable behavior, INTx asserted/deasserted path, endpoint reset on remove, TX done/TX stop/RX done/control IPC interrupts observed by firmware, and PM suspend/resume IRQ signaling.
