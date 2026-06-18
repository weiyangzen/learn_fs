# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.h Research

## Purpose
`adma.h` defines the software object model and PPC440SPe ADMA constants used by `adma.c`. It bridges the generic Linux dmaengine/async_tx types with the PPC440SPe DMA and XOR hardware descriptors declared in `dma.h` and `xor.h`.

## Important APIs, Types, and Functions
The conversion macros `to_ppc440spe_adma_chan()`, `to_ppc440spe_adma_device()`, and `tx_to_ppc440spe_adma_slot()` recover driver-private containers from generic dmaengine objects. Constants define engine IDs (`PPC440SPE_DMA0_ID`, `PPC440SPE_DMA1_ID`, `PPC440SPE_XOR_ID`), maximum byte counts, default RAID polynomial, operation threshold, and the RXOR-active bit.

`struct ppc440spe_adma_device` contains the parent `struct device`, mapped DMA/XOR/I2O register pointers, hardware id, coherent descriptor pool virtual and DMA addresses, pool size, IRQ numbers, and embedded `struct dma_device`. `struct ppc440spe_adma_chan` contains the channel lock, active chain, all-slot pool, last-used cursor, pending count, hardware-chain initialization flag, completion tasklet, helper pages, and helper DMA addresses. `struct ppc440spe_rxor` is a cursor for encoding RXOR source groups. `struct ppc440spe_adma_desc_slot` wraps one hardware descriptor, async_tx descriptor, list nodes, grouping metadata, source/destination counts, flags, RXOR reverse bits, RXOR cursor, and zero-sum/CRC result pointer.

## Control Flow
The header itself has no executable control flow, but its fields directly drive `adma.c` flows. Probe fills `ppc440spe_adma_device` and creates one `ppc440spe_adma_chan`. Channel resource allocation creates many `ppc440spe_adma_desc_slot` objects and attaches them to `all_slots`. Prepare functions form transaction groups through `group_list`, `group_head`, `slot_cnt`, and `slots_per_op`. Submit and completion move those slots through the channel `chain` and use flags such as `PPC440SPE_DESC_WXOR`, `PPC440SPE_DESC_RXOR`, `PPC440SPE_DESC_PCHECK`, and `PPC440SPE_DESC_QCHECK` to interpret hardware results.

## State and Persistence
All definitions describe in-memory kernel state. Descriptor slots persist for the lifetime of allocated channel resources and are reused across submitted transactions. Device and channel structures persist from probe until remove. The header does not define filesystem persistence or user-visible ABI, but the structures back the sysfs-driven RAID6 enable and polynomial state implemented in `adma.c`.

## Dependencies and Integration Points
This header includes Linux types plus the local hardware layout headers `dma.h` and `xor.h`. It integrates with dmaengine through embedded `struct dma_device`, `struct dma_chan`, and `struct dma_async_tx_descriptor`; with async_tx through descriptor flags and callback/cookie state; and with PowerPC PPC440SPe hardware through the DMA CDB and XOR CB storage referenced by `hw_desc`.

## Risks and Edge Cases
The descriptor metadata is compact and stateful. Incorrect `slot_cnt`/`slots_per_op` values can make cleanup free the wrong slots. `reverse_flags[8]` assumes enough bits for RXOR operand tracking across the supported descriptor layout. The union of zero-sum and CRC result pointers relies on operation flags to interpret it correctly. Engine IDs are used as array indices in `adma.c`, so they must stay aligned with `PPC440SPE_ADMA_ENGINES_NUM` and the global arrays.

## Test Signals
Build coverage for the PPC440SPe ADMA driver is the primary header test. Runtime evidence comes indirectly from descriptor allocation/reuse, successful dmaengine callbacks, RAID6 self-test, zero-sum result reporting, and absence of slot accounting assertions during mixed memcpy/XOR/PQ traffic.
