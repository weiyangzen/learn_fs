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
