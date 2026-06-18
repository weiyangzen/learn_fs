# sources/distributed-fs/ceph-client/drivers/parisc/iosapic_private.h

## Purpose
This private header defines the firmware routing-table and runtime state structures used exclusively by the PA-RISC I/O SAPIC driver.

## Important APIs, Types, And Functions
`struct irt_entry` describes 16-byte firmware I/O SAPIC routing entries: type, length, interrupt type, polarity/trigger, source PCI device/pin, source bus/segment, destination INTIN, and destination SAPIC address. Constants define IRT type/length, vectored interrupt value, polarity and trigger encodings, and masks for PCI source fields. `struct vector_info` stores per-INTIN runtime state. `struct iosapic_info` stores per-controller runtime state. Optional IA64-only SAPIC structures are retained under `__IA64__`.

## Control Flow
This header has no executable flow. `iosapic.c` fills `irt_entry` arrays from firmware, attaches one `vector_info` to each hardware INTIN, and links `iosapic_info` objects as LBAs register integrated SAPICs.

## State And Persistence
The declared structures hold persistent boot-time routing and runtime IRQ programming state. `vector_info` includes both firmware-derived routing (`irte`) and Linux/CPU IRQ data (`txn_irq`, `txn_addr`, `txn_data`, `eoi_addr`, `eoi_data`).

## Dependencies And Integration Points
The header is private to `drivers/parisc/iosapic.c` and mirrors PDC/PAT firmware table layout. Its fields feed Linux IRQ chip data and PCI IRQ fixup.

## Risks
The comments warn that structure field order matters for 64-bit packing. Any change to `struct irt_entry` layout can break direct firmware table decoding. Multi-cell support is stubbed but not active, so adding platforms with multiple routing tables would need structural changes.

## Test Signals
Compile-time structure layout and runtime IRT decoding are the primary signals. Debug dumps in `iosapic.c` should show expected 16-byte entries and matching SAPIC addresses/INTINs.
