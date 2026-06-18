# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_regs.h

Purpose: Defines EF10 architecture MMIO register offsets, descriptor/event bitfields, enumerators, workaround addresses, PIO aperture layout, and RX prefix offsets.

Important APIs and definitions: Includes register offsets such as `ER_DZ_EVQ_RPTR`, `ER_DZ_EVQ_TMR`, `ER_DZ_RX_DESC_UPD`, `ER_DZ_TX_DESC_UPD`, and `ER_DZ_TX_PIOBUF`; event fields for driver, MCDI, RX, and TX events; RX/TX descriptor bitfields for kernel descriptors, TX checksum/timestamp options, PIO, and TSO; indirect EVQ update definitions for bug 35388; and `ES_DZ_RX_PREFIX_*` offsets and size.

Control flow and integration: This header is consumed by low-level IO, event, RX, and TX code to pack/unpack hardware-visible qwords and owords with shared `EFX_POPULATE_*` and `EFX_*FIELD` macros. It has no executable flow.

State and persistence: No runtime state. The constants encode the hardware ABI and therefore form persistent compatibility with EF10 firmware and silicon revisions.

Dependencies: No external implementation, but naming conventions depend on SFC bitfield helpers and EF10 architecture semantics. Workaround constants are used by hardware-specific IO paths.

Risks: Any incorrect bit position, width, step, or row count corrupts hardware interaction. Duplicate field macro names across descriptor variants are intentional but can confuse readers. RX/TX queue sizing and event parsing depend on these constants matching hardware revision expectations.

Test signals: Hardware bring-up, descriptor DMA tests, event queue processing, TX/RX traffic, TSO/checksum offload validation, interrupt moderation, PIO TX, and regression tests on EF10 revisions affected by the indirect EVQ update workaround.
