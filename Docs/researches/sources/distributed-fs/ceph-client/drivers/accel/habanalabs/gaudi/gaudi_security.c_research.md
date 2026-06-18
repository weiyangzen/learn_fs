# Research: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_security.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000953`: lines 1-5151, `Docs/researches/chunks/subset-b-000953_research.md`
- `subset-b-000954`: lines 5152-10056, `Docs/researches/chunks/subset-b-000954_research.md`
- `subset-b-000955`: lines 10057-13079, `Docs/researches/chunks/subset-b-000955_research.md`

## Chunk Research

### subset-b-000953: lines 1-5151

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_security.c lines 1-5151

## Purpose
This chunk is the beginning of Gaudi ASIC security initialization for the HabanaLabs accelerator driver. It defines the register lists used later for LBW/HBW range-register programming, provides the low-level helper for writing per-register protection-bit pages, fully covers MME protection-bit setup, and covers most of DMA protection-bit setup through the first part of DMA7 core protection programming.

The code is hardware bring-up/security policy code, not a generic authorization layer. Its job is to translate a fixed Gaudi register security model into MMIO writes via `WREG32()`: protection bits are cleared for selected registers that should be protected, some full register blocks are marked protected, and selected MME/DMA control/status/error/queue-manager registers are given explicit protection masks.

## Important APIs, Types, And Data Tables
- `struct hl_device *hdev`: the device context passed through all helpers. In this chunk it is used mostly for `hdev->asic_prop.fw_security_enabled`, which selects whether some blocks are additionally protected when firmware security is disabled.
- `WREG32(addr, value)`: the main side-effect API. Every security setting in this chunk is a 32-bit MMIO write to either a real Gaudi register or a derived protection-bit register address.
- `CFG_BASE` and `PROT_BITS_OFFS`: address constants used to derive the protection-bit MMIO address for a 4 KiB register page.
- `GAUDI_NUMBER_OF_LBW_RR_REGS`, `GAUDI_NUMBER_OF_HBW_RR_REGS`, and `GAUDI_NUMBER_OF_LBW_RANGES`: array/range dimensions for later range-register programming.
- `gaudi_rr_lbw_*_regs[]`: LBW range-register address tables for write/read hit registers and min/max address registers. They cover DMA interface windows plus SIF/NIF router range protection registers.
- `gaudi_rr_hbw_*_regs[]`: HBW range-register address tables for write/read hit registers, base-low/high registers, and mask-low/high registers. They cover DMA downstream channels and SIF/NIF router controls.
- `gaudi_pb_set_block(hdev, base)`: helper that walks the protection-bit page for a register block and writes zero to each protection-bit word until the end of that 4 KiB page.
- `gaudi_init_mme_protection_bits(hdev)`: clears full MME ACC/SBAB/PRTN protection-bit blocks and then builds explicit masks for MME control and queue-manager registers.
- `gaudi_init_dma_protection_bits(hdev)`: starts DMA security setup, optionally protects selected DMA interface blocks when firmware security is disabled, clears QM/core protection-bit control words, and then builds per-register masks for DMA0-DMA7 QM and core windows. This chunk ends before the function is complete.

## Control Flow
The entry path for these lines is outside the chunk (`gaudi_init_security()` later in the file), which eventually calls protection-bit and range-register initializers. Within this chunk the control flow is straight-line hardware initialization:

1. Static arrays enumerate all LBW and HBW range-register MMIO addresses that later loops can program uniformly.
2. `gaudi_pb_set_block()` converts a register block base into a protection-bit-page address with `base - CFG_BASE + PROT_BITS_OFFS`, then writes zeros across the page until the low 12 bits wrap to the next 4 KiB block.
3. `gaudi_init_mme_protection_bits()` first clears broad MME protection-bit pages for ACC/SBAB/PRTN blocks and selected CTRL/QM protection-bit words. It then repeatedly computes:
   - `pb_addr = (register & ~0xFFF) + PROT_BITS_OFFS`
   - `word_offset = ((register & PROT_BITS_OFFS) >> 7) << 2`
   - `mask` as a bitset of 32-bit register slots inside the protection-bit word
   - `WREG32(pb_addr + word_offset, ~mask)`
4. The MME path applies this pattern to MME0 and MME2 QM registers, while comments state that MME1 and MME3 are slave MMEs whose whole QM blocks stay protected by range registers.
5. `gaudi_init_dma_protection_bits()` conditionally protects some DMA interface/downstream/PLL blocks when `fw_security_enabled` is false, then clears the last protection-bit word (`+ 0x7C`) for every DMA QM and core block.
6. The DMA path repeats the same computed-mask pattern for each DMA engine. The covered lines include complete QM setup for DMA0-DMA7 and core setup through DMA7's main RD/WR/error mask group; the chunk boundary cuts before the final DMA7 core status/debug masks and before the function closes.

## State And Persistence Behavior
There is no heap allocation, reference management, or software-owned persistent state in this chunk. The persistent state is hardware state: protection bits and range/protection registers retained by the Gaudi device until reset or reprogramming.

The important state transitions are:
- Writing zero to protection-bit pages marks all registers in that protection-bit word/block as protected according to the file comment later in the full source: default `1` means not protected, cleared bits mean protected.
- Writing `~mask` protects only the selected register slots in a protection-bit word while leaving unmasked slots unprotected.
- `fw_security_enabled` changes the amount of block-level DMA/MME protection performed. When firmware security is disabled, the driver protects additional DMA interface blocks itself.
- MME slave/master topology is encoded by omission: MME1 and MME3 QM blocks are not given detailed allow masks in this chunk because comments say their whole QM blocks are protected by range registers.

Because all writes are MMIO side effects, ordering matters: broad block protection, protection-bit control clearing, and per-register masks must be executed during device initialization before untrusted userspace workloads can interact with queues or engines.

## Dependencies
- `gaudiP.h` supplies HabanaLabs driver types/macros such as `struct hl_device`, device properties, and the `WREG32()` MMIO helper.
- `../include/gaudi/asic_reg/gaudi_regs.h` supplies all `mm...` Gaudi register constants used to derive protection-bit addresses.
- Hardware definitions such as `CFG_BASE`, `PROT_BITS_OFFS`, MME/DMA block base addresses, QM register offsets, and core register offsets must match the actual Gaudi register map.
- The later, out-of-chunk functions `gaudi_init_protection_bits()`, `gaudi_init_range_registers_lbw()`, `gaudi_init_range_registers_hbw()`, and `gaudi_init_security()` integrate these helpers into the full initialization sequence.
- Firmware security mode is supplied through `hdev->asic_prop.fw_security_enabled`, so firmware/boot discovery must set that property correctly before this code runs.

## Integration Points
- Device bring-up: these helpers are part of the Gaudi initialization path that establishes which registers can be accessed by secure/non-secure agents.
- MME command submission: MME QM registers for producer/consumer queues, completion queues, CP state, arbitration, message properties, and error reporting are explicitly protected.
- DMA command submission and data movement: DMA QM and DMA core protection bits protect queue configuration, queue pointers, command processor state, AXI user/security properties, RD/WR outstanding limits, rate limiting, error-reporting registers, and debug/status registers.
- Range-register setup: the static LBW/HBW arrays at the top are consumed by later range-register initializers, so this chunk provides shared data needed outside the visible helper bodies.
- Security error handling: although the acknowledgment routine is outside this chunk, the protected registers and hit registers initialized from this file determine which unauthorized accesses can be detected and reported.

## Risks
- The code is almost entirely hand-maintained register lists. A missing register in a `mask` expression can leave a sensitive control/status path unprotected; an extra register can break legitimate driver or firmware access.
- `word_offset` depends on `PROT_BITS_OFFS` bit arithmetic. If the register-map layout changes or a register is moved to a different protection-bit word, the generated address can silently target the wrong protection word.
- `~mask` writes all non-selected bits as `1`, so incorrectly grouped registers in the same word can unintentionally unprotect unrelated slots.
- `gaudi_pb_set_block()` assumes protection-bit pages occupy the last 128 bytes of each 4 KiB register block and that walking until `pb_addr & 0xFFF` becomes zero is correct for every supplied base.
- The chunk boundary cuts inside `gaudi_init_dma_protection_bits()`. Any final report must merge with the next chunk before claiming complete DMA protection behavior, especially for DMA7 core status/debug masks and the function exit.
- Security behavior diverges on `fw_security_enabled`. Tests or reviews that cover only one firmware-security mode can miss regressions in the other mode.
- Since this is init-time MMIO programming, many failures are observable only on real hardware or high-fidelity simulation; ordinary compile tests will not validate register address correctness.

## Test Signals
Useful validation signals for this chunk include:
- Successful Gaudi device initialization with both firmware-security-enabled and firmware-security-disabled configurations.
- No protection-bit or range-register RAZWI/security violations during normal MME and DMA queue setup, command submission, completion processing, and error handling.
- Expected protection faults for intentionally unauthorized accesses to protected MME/DMA QM/core registers.
- DMA transfers across all eight DMA engines continue to work after protection-bit initialization, including queue pointer updates, CP status reads, and completion/error paths.
- MME workloads using master MMEs 0 and 2 work while slave MME1/MME3 QM blocks remain inaccessible except through the intended protected/range-register paths.
- Hardware register dump comparison after init shows cleared protection bits only for the selected register slots and full-block protection for the blocks passed through `gaudi_pb_set_block()`.
- Regression checks should specifically inspect mask coverage for secure/non-secure property registers, AXI user registers, error-message address/data registers, debug registers, and rate-limit/outstanding-control registers.

### subset-b-000954: lines 5152-10056

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_security.c lines 5152-10056

## Purpose

This chunk is part of the Gaudi HabanaLabs accelerator security initialization code. It programs per-register protection bits for MMIO register blocks, making selected control, status, debug, queue-manager, and configuration registers accessible only to secure entities. The security model used by this file treats protection bits as inverted access controls: a set bit leaves the corresponding register accessible to any entity, while a cleared bit restricts it to secure access.

The assigned range starts near the end of `gaudi_init_dma_protection_bits()`, covers all of `gaudi_init_nic_protection_bits()`, and then covers the beginning of `gaudi_init_tpc_protection_bits()` through the `mmTPC1_CFG_OPCODE_EXEC` mask write. It is mostly a generated-style register protection table encoded as explicit `pb_addr`, `word_offset`, `mask`, and `WREG32()` sequences.

The highest-value behavior in this chunk is the NIC queue-manager coverage. It protects both queue managers for NIC0 through NIC4, including global queue-manager controls, producer and completion queue registers, command processor message and local-DMA registers, arbitration state, local range settings, indirect gateway registers, and error/status registers. The TPC section then applies the same queue-manager protection pattern to TPC0 and TPC1, plus the first TPC configuration-register protection groups.

## Important APIs, Types, And Functions

- `gaudi_init_nic_protection_bits(struct hl_device *hdev)`: complete in this chunk. It protects NIC queue-manager register blocks for `NIC0` through `NIC4`, both `QM0` and `QM1` for each NIC.
- `gaudi_init_tpc_protection_bits(struct hl_device *hdev)`: begins in this chunk. It optionally protects all TPC E2E credit blocks when firmware security is disabled, then protects `TPC0` and most of `TPC1` queue-manager/configuration registers before the chunk ends.
- `gaudi_init_dma_protection_bits(struct hl_device *hdev)`: the chunk starts inside the final `DMA7` core protection groups. The surrounding function began before this range and ends at line 5185.
- `struct hl_device`: passed through each helper. In this chunk it is used only by `gaudi_pb_set_block()` calls and by the `hdev->asic_prop.fw_security_enabled` gate in the TPC helper.
- `gaudi_pb_set_block(struct hl_device *hdev, u64 base)`: defined earlier in the file. It iterates over a block's protection-bit area and writes zeros, effectively securing all registers in that 4K block.
- `WREG32(addr, value)`: the driver MMIO write primitive used to program protection-bit words.
- `PROT_BITS_OFFS` and `CFG_BASE`: constants from the Gaudi register definitions and driver headers that map a normal register block to its protection-bit aperture.
- `mm...` register constants: generated Gaudi ASIC register offsets from `gaudi_regs.h`. This chunk uses `mmDMA7_*`, `mmNIC[0-4]_QM[0-1]_*`, `mmTPC[0-1]_QM_*`, `mmTPC[0-1]_CFG_*`, and `mmTPC[0-7]_E2E_CRED_BASE` constants.

## Control Flow

The runtime control flow is linear. `gaudi_init_security()` calls `gaudi_init_protection_bits()` after range-register setup. `gaudi_init_protection_bits()` calls the DMA, MME, NIC, and TPC protection helpers in sequence. This chunk covers the tail of the DMA helper, all of the NIC helper, and the first part of the TPC helper.

Each register group follows the same protection-bit calculation:

1. Pick a representative register in a 4K MMIO register block.
2. Compute `pb_addr = (register & ~0xFFF) + PROT_BITS_OFFS`, which targets the protection-bit area for that register block.
3. Compute `word_offset = ((register & PROT_BITS_OFFS) >> 7) << 2`, using address bits 7-11 to select the 32-bit protection word within the 128-byte protection-bit area.
4. Build `mask` by ORing `1U << ((register & 0x7F) >> 2)` for every register protected by the same protection word.
5. Write `~mask` to `pb_addr + word_offset` with `WREG32()`, clearing the bits for protected registers and leaving non-listed bits set.

At the start of each NIC and TPC queue-manager block, the helper writes zero to `base - CFG_BASE + PROT_BITS_OFFS + 0x7C`. That is the last 32-bit word of the 128-byte protection-bit area and secures the protection bits themselves for the queue-manager/configuration block.

`gaudi_init_nic_protection_bits()` repeats a nearly identical protection sequence for ten queue managers: `NIC0_QM0`, `NIC0_QM1`, `NIC1_QM0`, `NIC1_QM1`, `NIC2_QM0`, `NIC2_QM1`, `NIC3_QM0`, `NIC3_QM1`, `NIC4_QM0`, and `NIC4_QM1`. For each queue manager, the protected groups include:

- Global configuration, protection, secure/non-secure property, status, and message-enable registers.
- PQ base/size/PI/CI/config/status and ARUSER registers.
- CQ pointer/size/control/status and interface FIFO counters.
- Command processor message base, LDMA size/source/destination offset, status/current-instruction, barrier, debug, ARUSER, and AWUSER registers.
- Arbiter configuration, master credit, choice/push offset, status, error, message, and CGM registers.
- Local range, strict priority, rate-limit, AXCACHE, indirect APB gateway, global error address/data, and memory-init-busy registers.

`gaudi_init_tpc_protection_bits()` first checks `!hdev->asic_prop.fw_security_enabled`. In that mode it calls `gaudi_pb_set_block()` for all eight TPC E2E credit blocks, making the entire E2E credit register blocks secure-only. After that, this chunk protects `TPC0_QM` and `TPC0_CFG`, then protects `TPC1_QM` and the first `TPC1_CFG` groups. The chunk ends immediately after writing the `TPC1_CFG_PROT` protection word; the next group beginning at `TPC1_CFG_TSB_CFG_MAX_SIZE` is outside the requested range.

## State And Persistence Behavior

This code does not allocate memory, store driver-owned software state, or persist anything to disk. Its persistent effect is in hardware state: it writes the Gaudi device's protection-bit MMIO registers. Those settings remain effective until hardware reset, firmware reconfiguration, or another security initialization pass changes the same protection bits.

The `mask` and `word_offset` locals are temporary calculation state. The only input-dependent branch in this chunk is the TPC E2E credit block handling. When `hdev->asic_prop.fw_security_enabled` is false, the driver proactively secures the TPC E2E credit blocks itself; when firmware security is enabled, the driver leaves those blocks to firmware policy and continues with the explicit per-register protection writes.

Because `WREG32(pb_addr + word_offset, ~mask)` writes an entire 32-bit protection word, each group is stateful at word granularity. The helper relies on each listed group containing all registers that should remain protected in that word; any omitted register in the same word is left unprotected by this write unless it was protected by another write. The explicit zero writes to the `+0x7C` protection-bit word secure the protection-bit metadata itself.

## Dependencies

This code depends on the HabanaLabs driver MMIO infrastructure and the Gaudi register map:

- `gaudiP.h` provides Gaudi driver types, device properties, base address constants, and register access helpers.
- `../include/gaudi/asic_reg/gaudi_regs.h` provides the generated `mm...` register constants used to compute protection-bit positions.
- The hardware protection-bit layout documented in `gaudi_init_protection_bits()` later in the file is assumed by every calculation in this chunk: 4K register blocks, last 128 bytes as protection bits, address bits 7-11 selecting the word, and bits 2-6 selecting the bit.
- `WREG32()` must perform ordered 32-bit MMIO writes suitable for early device initialization.
- `hdev->asic_prop.fw_security_enabled` coordinates driver-owned security initialization with firmware-owned security policy.

The chunk also depends on surrounding initialization order. Range registers are initialized before protection bits in `gaudi_init_security()`, and the NIC/TPC helpers run after DMA/MME protection setup. If the security initialization order changes, some early MMIO accesses used by later bring-up code could become blocked before their setup completes.

## Integration Points

The integration entry point is `gaudi_init_security(struct hl_device *hdev)`, which is the Gaudi driver hook that initializes the device security model. The function first programs range registers for low-bandwidth and high-bandwidth access filtering, then calls `gaudi_init_protection_bits()`. This chunk's helpers are internal pieces of that protection-bit phase.

NIC integration is with the Gaudi NIC queue-manager blocks. Protecting `QM0` and `QM1` for every NIC constrains access to queue descriptors, doorbell/control metadata, command processor message bases, local DMA offsets, and arbitration/credit state. These are sensitive because a non-secure writer could otherwise redirect queues, change AXI user attributes, modify message destinations, or inspect internal execution state.

TPC integration is with tensor processor command submission and configuration. The queue-manager registers mirror the same command processor and arbitration surfaces as the NIC queue managers. The TPC configuration registers covered here include protection, flags, base-address/subtract configuration, stall controls, instruction cache base, rate limits, interrupt cause/mask, work-queue credits, AXI user fields, and opcode execution controls.

The final per-file reconciliation needs to stitch this chunk to the preceding and following chunks: the first lines complete a DMA7 core register group that starts before line 5152, and the last line stops before the rest of `TPC1_CFG` and later TPC2-TPC7 protection entries.

## Risks And Edge Cases

- The code is security-sensitive and write-only. A wrong register constant, mask bit, or protection-word address can silently leave a register accessible to non-secure agents or accidentally block a register required by normal driver operation.
- The chunk starts mid-mask in `gaudi_init_dma_protection_bits()`. A line-bounded review must not infer the full DMA7 write from this chunk alone; the initial `pb_addr`, `word_offset`, and earlier mask bits are in the previous range.
- The chunk ends mid-function in `gaudi_init_tpc_protection_bits()`. `TPC1_CFG_TSB_CFG_MAX_SIZE` and later `TPC1`/`TPC2`-through-`TPC7` protection writes continue outside this chunk.
- The repeated NIC queue-manager blocks are manually expanded. Copy/paste drift is the main maintenance risk: one NIC/QM instance may miss a register that the others protect, or may use a register from the wrong NIC/QM namespace.
- Several writes use `~mask` without explicit width casting. In C this is assigned to the 32-bit MMIO write path, but reviewers should preserve the intended 32-bit protection-word semantics if refactoring.
- `mask` is a `u32`; the bit calculation assumes `(register & 0x7F) >> 2` is in the 0-31 range. That follows from the documented protection-bit layout, but the code has no runtime validation for malformed register constants.
- A full 32-bit word is rewritten at each `WREG32()`. If two logical groups share a protection word, the later write must include all bits that should be cleared for that word. Splitting or reordering groups without checking word overlap can weaken protection.
- The `fw_security_enabled` branch means test coverage must consider both firmware-owned and driver-owned security modes. Only the non-firmware-security path secures all TPC E2E credit blocks in this helper.
- Hardware bring-up can fail in non-obvious ways if protection is enabled before firmware or the driver has finished writing required setup registers. Initialization ordering is therefore part of the security contract.

## Test Signals

Useful validation signals for this chunk are mostly hardware and driver bring-up signals:

- Gaudi initialization should complete in both `fw_security_enabled` modes, with no MMIO access faults during NIC and TPC bring-up after protection bits are programmed.
- Non-secure access attempts to protected NIC QM and TPC QM/CFG registers should be rejected or return the expected protected-access signature according to the platform security model.
- Secure firmware or privileged driver paths should still be able to access protected registers needed for diagnostics, reset, queue-manager setup, error handling, and debug collection.
- NIC queue setup, command submission, completion handling, local DMA message handling, arbitration, and error reporting should still function after all `NIC0`-`NIC4` `QM0`/`QM1` protection writes.
- TPC command submission, stall control, interrupt reporting, queue credits, opcode execution controls, and work-queue counters should remain operational for TPC0 and TPC1 after the covered protection writes.
- Register-dump or hardware-security tests should compare the protection-bit words for all repeated NIC queue managers and detect asymmetry between NIC instances or between `QM0` and `QM1`.
- Fault-injection tests should exercise RAZWI/protection-bit violations for representative registers from each protected category: global controls, PQ/CQ, CP message bases, LDMA offsets, ARB credits/status, local range, indirect gateway, error registers, TPC config flags, and debug-memory registers.
- Static review scripts can mechanically recompute `pb_addr`, `word_offset`, and bit positions from the `mm...` constants and flag duplicate/missing bits or protection-word overlap not represented in a single mask.

### subset-b-000955: lines 10057-13079

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
