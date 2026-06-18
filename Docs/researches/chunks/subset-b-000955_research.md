# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_security.c lines 10057-13079

## Scope

This chunk is the final security-initialization slice of the Gaudi Habana Labs accelerator driver security file. It starts in the tail of `gaudi_init_tpc_protection_bits()` while finishing TPC1 CFG protection bits, covers the full generated-style protection-bit programming for TPC2 through TPC7, and then defines the top-level protection-bit and range-register initialization helpers used by `gaudi_init_security()`.

The code is not Ceph filesystem logic despite living under the Ceph-client source snapshot. It is Linux kernel accelerator-driver register programming for the first-generation Gaudi ASIC security model.

## Purpose

The chunk configures which device registers and address ranges are accessible from non-secure or user-controlled initiators during Gaudi initialization. The major responsibilities are:

- Mark sensitive TPC queue-manager and TPC CFG registers as secure-only by clearing their protection bits.
- Lock the protection-bit storage for each TPC QM/CFG 4 KiB register block by clearing the protection bits that protect the PB registers themselves.
- Initialize global protection policy across DMA, MME, NIC, and TPC blocks through `gaudi_init_protection_bits()`.
- Program low-bandwidth and high-bandwidth range registers that gate access to internal register windows, DRAM, SRAM, firmware scratch areas, SPI flash, and optionally host memory.
- Apply a firmware-security-dependent Gaudi erratum workaround before the broader security setup runs.

The net effect is an early boot security boundary: register protection bits decide who may touch privileged device CSRs, while range registers decide which memory/address windows are considered protected.

## Important APIs, Types, And Functions

`gaudi_init_tpc_protection_bits(struct hl_device *hdev)` begins earlier in the file and ends in this chunk. The visible portion clears protection bits for TPC2 through TPC7 and finishes a TPC1 CFG group. Each protected register group computes:

- `pb_addr = (register & ~0xFFF) + PROT_BITS_OFFS`
- `word_offset = ((register & PROT_BITS_OFFS) >> 7) << 2`
- `mask` as one bit per protected 32-bit register in the relevant 4 KiB CSR block
- `WREG32(pb_addr + word_offset, ~mask)` to clear the selected protection bits

`gaudi_init_protection_bits(struct hl_device *hdev)` is the local coordinator for PB programming. It documents the PB address mapping: each 4 KiB register block reserves its last 128 bytes for 1024 protection bits, bits 7-11 select a PB word, and bits 2-6 select the bit within that word. A cleared bit means secure-only access, while a set bit allows non-secure access. When firmware security is disabled, it first secures several PLL PB blocks via `gaudi_pb_set_block()`, then calls the DMA, MME, NIC, and TPC PB initializers.

`gaudi_init_range_registers_lbw(struct hl_device *hdev)` programs LBW range registers for `GAUDI_NUMBER_OF_LBW_RANGES` ranges across `GAUDI_NUMBER_OF_LBW_RR_REGS` register banks. It fills start/end arrays with masked 26-bit LBW addresses and writes all hit, min, and max registers for AW and AR paths.

`gaudi_init_range_registers_hbw(struct hl_device *hdev)` programs HBW range registers across `GAUDI_NUMBER_OF_HBW_RR_REGS` banks. It uses `struct gaudi_device *gaudi = hdev->asic_specific` to decide whether host protection needs explicit range programming when `HW_CAP_MMU` is not initialized.

`gaudi_init_security(struct hl_device *hdev)` is the exported entry point in this chunk. It applies the GAUDI0500 workaround when `fw_security_enabled` is false, then calls LBW range setup, HBW range setup, and PB setup.

`gaudi_ack_protection_bits_errors(struct hl_device *hdev)` is an exported no-op stub in this chunk. The function exists as an integration hook but does not acknowledge or clear any hardware error state here.

## TPC Protection-Bit Programming

The TPC portion is large and repetitive. The visible range contains 121 `WREG32(pb_addr + word_offset, ~mask)` protection-bit writes and 12 direct writes to the per-block PB self-protection words for TPC2 through TPC7 QM/CFG blocks. TPC2, TPC3, TPC4, TPC5, TPC6, and TPC7 each follow the same structure:

- Clear the last PB-control word for the TPC QM and TPC CFG blocks with `WREG32(mmTPCx_QM_BASE - CFG_BASE + PROT_BITS_OFFS + 0x7C, 0)` and the matching CFG base. This secures the PB registers themselves.
- Protect QM global configuration and status registers, including secure/non-secure property registers and message-enable/status registers.
- Protect producer-queue registers: base addresses, sizes, producer/consumer indices, queue configuration, ARUSER properties, and PQ status.
- Protect completion-queue registers: status, pointer, transfer-size, control, IFIFO count, and command-processor message base-address registers.
- Protect command-processor registers: LDMA offset registers, CP status/current instruction registers, barrier configuration, debug registers, and ARUSER/AWUSER fields.
- Protect arbiter configuration, credit, message, error, and status registers.
- Protect local range, CGM/rate-limit, AXCACHE, indirect gateway, global error, and memory-init status registers.
- Protect TPC CFG registers: round CSR, CFG protection and flag registers, address-high/subtract values, stall/rate/MSS/interrupt/WQ/user/opcode controls, TSB max size, debug memory registers, inflight counters, IRQ occupancy counters, and functional MBIST registers.

The chunk begins with the last TPC1 CFG protection group, so the full TPC1 setup belongs to the previous chunk. The merge lane should reconcile that boundary before producing a file-level summary.

## Range Register Programming

The LBW range setup defines 10 protected or security-relevant low-bandwidth windows by masking hard-coded physical-like addresses with `0x3FFFFFF` and using open-boundary style start/end values (`start = base - 1`, `end = last + 1`). It enables every LBW range hit bit for both AW and AR on all 28 LBW range-register banks using `(1 << GAUDI_NUMBER_OF_LBW_RANGES) - 1`, then writes each range start/end to the corresponding min/max AW and AR registers.

The HBW range setup defines up to six high-bandwidth windows for every HBW security register bank:

- Range 0: first 512 MiB of DRAM, using `DRAM_PHYS_BASE`, low mask `0xE0000000`, and high mask `0x3FFFF`.
- Range 1: first 128 bytes of SRAM, using `SRAM_BASE_ADDR`; only AW registers are programmed for this range, matching the comment that it is read-only for user-visible tensor DMA behavior.
- Range 2: PSOC scratchpad, using `PSOC_SCRATCHPAD_ADDR` and a `0xFFFF0000` low mask.
- Range 3: PCIe firmware SRAM, using `PCIE_FW_SRAM_ADDR` and a `0xFFFF8000` low mask.
- Range 4: SPI flash, using `SPI_FLASH_BASE_ADDR` and a `0xFE000000` low mask.
- Range 5: host memory, programmed only if `HW_CAP_MMU` is absent from `gaudi->hw_cap_initialized`.

HBW hit registers are set to `0x1F` for writes and `0x1D` for reads. That enables ranges 0, 1, 2, 3, and 4 for AW, but omits range 1 from AR. If the MMU is not initialized, host memory is explicitly protected with zero base and low mask plus high mask `0xFFF80`.

## Control Flow

The top-level flow in this chunk is simple:

1. `gaudi_init_security()` optionally applies firmware-security-disabled errata writes to MME SBAB/ACC protection-property registers and a RAZWI diagnostic behavior register.
2. `gaudi_init_range_registers_lbw()` programs LBW hit/min/max registers.
3. `gaudi_init_range_registers_hbw()` programs HBW hit/base/mask registers and optionally host-memory protection.
4. `gaudi_init_protection_bits()` initializes PBs for PLL blocks when firmware security is disabled, then delegates to DMA, MME, NIC, and TPC PB initializers.
5. The TPC initializer uses a repeated local sequence of address calculation, bit-mask aggregation, and PB writeback for each protected TPC register group.

There is no retry path, error return, or verification readback. All helpers are `void` and assume MMIO writes succeed.

## State And Persistence Behavior

The only persistent state changed by this chunk is device hardware state reached through `WREG32()`. No kernel heap state, filesystem state, firmware blob, or persistent host-side data structure is modified.

The programmed state remains in Gaudi hardware registers until reset, reinitialization, firmware action, or another driver path changes those registers. Protection bits are treated as default-open at reset: the comments state all PBs default to 1, meaning unprotected, and initialization clears selected bits to make those registers secure-only.

The code reads persistent driver capability/configuration state from:

- `hdev->asic_prop.fw_security_enabled`, which controls whether the host driver must program additional security properties instead of relying on secure firmware.
- `hdev->asic_specific`, cast to `struct gaudi_device`, and `gaudi->hw_cap_initialized & HW_CAP_MMU`, which controls whether host-memory HBW range protection is explicitly programmed.

Because there is no readback or cached mirror, the software source of truth after initialization is the code and hardware programming sequence rather than an in-memory policy object.

## Dependencies And Integration Points

This chunk depends on the Habana Labs register definition headers for `mmTPC*`, `mmMME*`, range-register, base-address, and protection-offset constants. It also depends on driver MMIO helpers/macros such as `WREG32()`, address helpers `lower_32_bits()` and `upper_32_bits()`, and hardware constants including `CFG_BASE`, `PROT_BITS_OFFS`, `DRAM_PHYS_BASE`, `SRAM_BASE_ADDR`, `PSOC_SCRATCHPAD_ADDR`, `PCIE_FW_SRAM_ADDR`, and `SPI_FLASH_BASE_ADDR`.

The range-register helpers use register-address arrays defined earlier in `gaudi_security.c`, including LBW AW/AR hit, min, and max arrays and HBW AW/AR hit, base-low, base-high, mask-low, and mask-high arrays. The protection-bit coordinator integrates with helper functions defined earlier in the file: `gaudi_pb_set_block()`, `gaudi_init_dma_protection_bits()`, `gaudi_init_mme_protection_bits()`, `gaudi_init_nic_protection_bits()`, and the full `gaudi_init_tpc_protection_bits()`.

The primary external integration point is Gaudi device bring-up. Other Gaudi driver initialization code should call `gaudi_init_security()` after MMIO access is available and before user workloads or untrusted command submission can access device engines. `gaudi_ack_protection_bits_errors()` is an external hook for PB error handling, but in this implementation it intentionally does nothing.

## Risks And Edge Cases

The generated-style PB programming is fragile because every register constant participates in bit arithmetic. A wrong `mmTPCx_*` register, missing mask bit, wrong base register for `pb_addr`, or incorrect `word_offset` can silently leave a privileged CSR accessible or accidentally secure a register that non-secure software needs.

The TPC blocks are nearly identical but manually expanded. Copy/paste drift between TPC2 through TPC7 is a real maintenance risk. The visible counts are symmetric for TPC2-TPC7, but a future register addition must be applied consistently across all TPC instances and across the adjacent chunk that contains TPC0/TPC1 setup.

`WREG32(pb_addr + word_offset, ~mask)` relies on the PB register convention where cleared bits mean protected. This inverted write can be misread during maintenance: adding a register to `mask` removes non-secure access, while omitting it leaves access open.

The self-protection writes to `PROT_BITS_OFFS + 0x7C` are security-critical. If omitted for a block, software may correctly protect target registers but leave the PB words themselves writable by a non-secure entity.

The LBW ranges use hard-coded addresses and boundary arithmetic. Off-by-one or address-map changes could either expose protected MMIO windows or overprotect legitimate accesses. The HBW range setup similarly depends on base/mask semantics that are not locally validated.

The `HW_CAP_MMU` conditional changes host-memory protection behavior. If the capability bit is set too early, stale, or incorrect, the function skips explicit host protection. If it is not set when MMU-mediated protection is actually active, the code may program redundant or conflicting host range entries.

The function has no error handling or readback, so hardware posting, blocked MMIO, incorrect register definitions, or reset races would not be detected here. Failures surface later as security violations, RAZWI behavior, command submission failures, or inaccessible registers.

## Test Signals

High-signal validation is hardware or emulator bring-up that calls `gaudi_init_security()` and then checks both access behavior and register contents:

- Read back representative TPC2-TPC7 PB words and verify that bits for QM globals, PQ/CQ/CP/arbiter/local-range/CFG/debug/MBIST registers are cleared while unrelated bits remain as expected.
- Confirm that PB self-protection words for each TPC2-TPC7 QM and CFG block are zeroed at `PROT_BITS_OFFS + 0x7C`.
- Exercise non-secure/user accesses to protected TPC registers and verify they fault, return expected RAZWI values, or are otherwise denied according to the platform security model.
- Verify secure firmware or secure driver paths can still access the protected registers needed for initialization and diagnostics.
- Validate LBW range-register contents for all 28 banks: hit masks should enable all 10 ranges, and min/max AW/AR values should match the hard-coded range arrays.
- Validate HBW range-register contents for all 24 banks: hit masks should be `0x1F` for AW and `0x1D` for AR, base/mask pairs should match DRAM/SRAM/scratch/PCIe-FW/SPI definitions, and host range entries should be present only when `HW_CAP_MMU` is not initialized.
- Test both `fw_security_enabled` states. With firmware security disabled, the MME GAUDI0500 workaround writes and PLL PB block protection should be observable; with firmware security enabled, those host-side writes should be skipped.

Regression indicators include RAZWI events on expected legal accesses, successful non-secure writes to privileged TPC CSRs, user workload failures after PB setup, firmware initialization failures due to overprotected registers, or inconsistent PB state between TPC instances.
