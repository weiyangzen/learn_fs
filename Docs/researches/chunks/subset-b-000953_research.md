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
