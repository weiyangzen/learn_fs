# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2P.h

## Purpose
This private Gaudi2 header centralizes ASIC-specific constants, resource counts, hardware capability masks, engine and interrupt identifiers, private driver state, and local function declarations used by the HabanaLabs Gaudi2 driver. It is the shared contract between Gaudi2 implementation files, including the CoreSight path, queue setup, memory mapping, security, block initialization, and event handling.

## Important APIs, types, and functions
- Firmware and timeout constants name the Linux and boot FIT images and define CPU, preboot, boot FIT, and CoreSight wait durations.
- Queue counts derive `NUMBER_OF_HW_QUEUES` and `NUMBER_OF_QUEUES` from PDMA, EDMA, MME, TPC, NIC, ROT, CPU, and `NUM_OF_PQ_PER_QMAN`.
- User mapping constants derive the size and index layout of `mapped_blocks`, including ARC, ACP, NIC UMR, decoder, and exposed sync-manager blocks.
- Memory-map constants describe firmware image, page-table, EDMA scratchpad, host VA, HBM VA, and internal CB sizing.
- Hardware capability masks encode initialized or available engines: PLL, DRAM, PMMU, CPU, MSI-X, CPU queue, clock gate, KDMA, DMMU bits, PDMA, EDMA, MME, ROT, HBM scrambler, decoder, TPC, NIC, and combined MMU masks.
- `enum gaudi2_reserved_sob_id`, `enum gaudi2_reserved_mon_id`, and `enum gaudi2_reserved_cq_id` reserve sync objects, monitors, and completion queues for CS completion, KDMA completion, and decoder normal/abnormal completion handling.
- Engine identity enums define DMA cores, rotators, MMEs, TPCs, decoders, HBMs, and EDMAs in driver-facing order.
- `enum gaudi2_irq_num` maps event queue, decoder interrupts, completion, NIC port interrupts, TPC assert, EQ error, user interrupts, reserved interrupts, unexpected error, and the final MSI-X index.
- `struct dup_block_ctx` carries a repeated-block initialization callback and addressing stride data.
- `struct gaudi2_queues_test_info` holds DMA and kernel addresses for queue self-test messages.
- `struct gaudi2_device` is the private per-device state extension hung off `hdev->asic_specific`.
- Function declarations expose Gaudi2 helpers including TPC iteration, CoreSight init/debug/halt, duplicated-block init, HMMU enable checks, range-register writes, security setup/error handling, and device activity reporting.

## Control flow
The header has no executable control flow, but many macros determine runtime control flow in implementation files. Queue and reserved-resource counts size loops and arrays; hardware capability masks gate initialization and error paths; IRQ enum ordering drives MSI-X allocation and event dispatch; `GAUDI2_ENG_ID_TO_STR` and `GAUDI2_QUEUE_ID_TO_STR` convert hardware identifiers defensively by returning `"not found"` when indexes exceed the known enum ranges. The `static_assert` after the IRQ enum ensures user interrupt numbering starts after the shared decoder interrupt range.

## State and persistence behavior
`struct gaudi2_device` defines the major persistent in-kernel state for the ASIC instance. It stores the CPU-CP information callback, user-mappable block table, MME random seeds, hardware queue lock, scratchpad memory, virtual MSI-X doorbell page, current DRAM BAR address, initialized hardware-capability bitmaps, active ARC bitmaps, per-engine decoder/TPC/NIC capability bitmaps, hardware event validity and histogram arrays, and queue-test buffers. These fields survive across normal driver operations and are reset or cleared by implementation code during engine reset, capability discovery, event processing, or teardown.

## Dependencies and integration points
The file depends on Linux/HabanaLabs UAPI and internal generated Gaudi2 headers: DRM accel UAPI, common driver definitions, boot interface, Gaudi2 registers, packet formats, firmware interface, and async events. It is included by Gaudi2 implementation files that need common ASIC sizing and private state. `gaudi2_coresight_regs.h` includes this header for `CORESIGHT_TIMEOUT_USEC`, `HW_CAP_PMMU`, `MMUBP_ASID_MASK` through the masks dependency chain, and `struct gaudi2_device` used by CoreSight address validation.

## Risks and edge cases
- Many constants derive from generated register symbols; a generated header mismatch can silently corrupt resource counts, register spacing assumptions, or reserved object ranges.
- `NUM_USER_MAPPED_BLOCKS` and related start indexes must stay aligned with code that fills `mapped_blocks`; changing NIC, decoder, ARC, or sync-manager counts can break user mappings.
- Hardware capability masks use fixed bit positions, so firmware and diagnostic code must agree on bit layout.
- `HW_CAP_RESERVED` uses `BIT(43)` instead of `BIT_ULL(43)`, which is suspicious for a bit above 31 unless `BIT` is widened in this build context.
- `enum substitude_tpc` keeps a misspelled name and comments documenting replacement TPC behavior; renaming would affect all users.
- `struct gaudi2_device` is broad shared state, so additions require careful reset, teardown, and concurrency treatment.

## Test signals
Useful validation signals include successful Gaudi2 probe, queue count and MSI-X allocation consistency, no compile-time assertion failure for interrupt ordering, correct user block mmap behavior, hardware capability masks matching discovered engines, successful CoreSight init with expected masks, queue self-tests using `queues_test_info`, and reset paths clearing initialized and active capability bits without losing persistent event statistics unexpectedly.
