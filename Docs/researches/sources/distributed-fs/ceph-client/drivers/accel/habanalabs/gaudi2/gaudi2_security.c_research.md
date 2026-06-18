# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_security.c

## Purpose

`gaudi2_security.c` is the Gaudi2-specific security policy table and programming sequence for the HabanaLabs accelerator driver. It defines which Gaudi2 register blocks are protected by protection bits, which user-visible registers/ranges are deliberately left unprotected, and which address windows are blocked by LBW, HBW, and MMU range registers. The file also provides the Gaudi2 hooks used by the common security layer to initialize protection and to print/acknowledge protection-bit violations.

The file is mostly declarative hardware inventory: static arrays name base blocks and per-block exception registers for SFT, HIF, routers, HMMUs, CPU/PSOC, DMA engines, MMEs, TPCs, SRAM, sync managers, ARC schedulers, XBARs, NICs, rotators, PCIe, PMMU/PLL, thermal, and HBM. The executable tail translates these tables into writes to `GLBL_SEC` arrays and range-register windows.

## Important APIs, types, and data

- `struct rr_config` carries a range-register write request: minimum address, maximum address, register index, and range type (`RR_TYPE_SHORT`, `RR_TYPE_LONG`, and privileged variants from `gaudi2P.h`).
- `struct gaudi2_atypical_bp_blocks` describes blocks whose protection-bit layout is not handled by the common `HL_BLOCK_GLBL_SEC_*` helpers. It is used for sync manager object protection bits.
- `struct gaudi2_tpc_pb_data`, `struct gaudi2_tpc_arc_pb_data`, and `struct gaudi2_ack_pb_tpc_data` are small iterator payloads passed through `struct iterate_module_ctx` so TPC handling can reuse `gaudi2_iterate_tpcs()`.
- `UNSET_GLBL_SEC_BIT()` sets a bit in a local `GLBL_SEC` bitmap. In this security encoding, zero means protected and one means unprotected, so setting a bit marks a register/object as user-accessible.
- The large `gaudi2_pb_*` arrays are the policy surface. Base arrays list block bases to protect; `*_unsecured_regs` arrays list individual registers to unprotect; `*_unsecured_regs[]` with `struct range` lists contiguous unprotected register spans.
- Exported/non-static functions are `gaudi2_init_security()`, `gaudi2_ack_protection_bits_errors()`, `gaudi2_pb_print_security_errors()`, and `gaudi2_write_rr_to_all_lbw_rtrs()`.

## Control flow

Initialization enters through `gaudi2_init_security(hdev)`. It first calls `gaudi2_init_protection_bits()` and aborts on any non-zero accumulated return code. If protection-bit programming succeeds, it calls `gaudi2_init_range_registers()` to install LBW, HBW, and MMU address-deny ranges.

`gaudi2_init_protection_bits()` walks every hardware family. For normal repeated blocks it calls common helpers such as `hl_init_pb()`, `hl_init_pb_with_mask()`, `hl_init_pb_ranges()`, and single-dcore variants. Those helpers allocate an array of `struct hl_block_glbl_sec`, zero it to protect every register, clear selected bits for the allowed registers/ranges, and write the resulting `GLBL_SEC` words to each enabled block instance. Enabled-instance masks from `hdev->asic_prop` and `hdev->nic_ports_mask` prevent writes to disabled HIF/HMMU, EDMA, XBAR edge, DRAM/HBM, and NIC instances.

TPC programming is custom. `gaudi2_init_pb_tpc()` builds one protection bitmap from `gaudi2_pb_dcr0_tpc0`, unsecures normal TPC/QM registers, unsecures every kernel tensor and QM tensor by applying computed tensor strides, unsecures 32 QM SRF registers, unsecures four lock-value registers, then applies the result to all live TPCs through `gaudi2_iterate_tpcs()`. `gaudi2_init_pb_tpc_arc()` similarly iterates TPC ARC ranges and stores errors in the iterator context.

Sync manager object programming is also custom. `gaudi2_init_pb_sm_objs()` allocates a raw security-word array for the sync-manager object space, unsecures selected SOB and monitor object classes after the reserved command-submission region, writes the tailored Dcore0 array, then writes all-ones arrays to Dcore1-Dcore3 to unsecure their corresponding objects.

Range-register programming is split by fabric. `gaudi2_init_lbw_range_registers_secure()` defines short LBW windows for NIC configuration and optional PSOC ranges, plus long windows for TPC debug and PCIe DBI MSI-X doorbell. It calls `gaudi2_write_rr_to_all_lbw_rtrs()` so each range is written to SFT LBW routers, DCORE routers, and PCIe ELBI/MSTR/LBW router blocks. `gaudi2_init_hbw_range_registers()` installs an HBW short range covering SPI flash, ARC memories, boot ROM, firmware scratchpad/SRAM regions, and similar firmware-reserved areas across SFT/SIF/PCIe master interfaces. `gaudi2_init_mmu_range_registers()` protects the reserved DRAM area from `DRAM_PHYS_BASE` through `dram_user_base_address`, using `hdev->asic_funcs->scramble_addr()` because these registers sit after HMMU address scrambling.

Error handling enters through `gaudi2_ack_protection_bits_errors()`, which mirrors most initialization block lists and calls `hl_ack_pb*()` helpers. The common helper reads each block's `HL_BLOCK_GLBL_ERR_CAUSE` and `HL_BLOCK_GLBL_ERR_ADDR`, calls the ASIC `pb_print_security_errors` callback, then writes the cause back to clear it. Gaudi2's printer, `gaudi2_pb_print_security_errors()`, decodes APB privileged/security/unmapped read/write causes plus external security/unmapped writes and emits a rate-limited error.

## State and persistence behavior

The only persistent state affected by this file is device hardware state. Initialization writes protection-bit arrays and range-register min/max fields into MMIO registers via `WREG32()`. Error acknowledgement reads and clears MMIO cause registers. The file does not write repository files, firmware images, or host-side persistent configuration.

Host memory allocations are temporary. `gaudi2_init_pb_tpc()` and common helper calls allocate protection-bit arrays, write them to hardware, and free them. `gaudi2_init_pb_sm_objs()` allocates a raw security array and frees it after programming. There is no long-lived cache in this file; repeated initialization after reset reconstructs policy from static tables.

Security behavior depends on runtime device properties. If `hdev->asic_prop.fw_security_enabled` is true, several CPU, PSOC, PLL, and thermal blocks are skipped because firmware/privileged range registers already protect them. Masks such as `hmmu_hif_enabled_mask`, `edma_enabled_mask`, `xbar_edge_enabled_mask`, `dram_enabled_mask`, and `nic_ports_mask` determine which instances are actually programmed or acknowledged.

## Dependencies and integration points

The file depends on `gaudi2P.h` for topology constants, range-register type constants, `struct dup_block_ctx`, iterator declarations, and ASIC helper prototypes. It depends on generated Gaudi2 register headers for thousands of `mm*` base and register constants. It relies on common security helpers in `common/security.c` for generic protection-bit bitmap construction, block lookup, hardware writes, and violation acknowledgement.

`gaudi2.c` calls `gaudi2_init_security()` in late initialization and compute-reset late initialization after ARC setup/scrubbing. The Gaudi2 ASIC function table wires `.pb_print_security_errors = gaudi2_pb_print_security_errors`, `.ack_protection_bits_errors = gaudi2_ack_protection_bits_errors`, and `.scramble_addr = gaudi2_mmu_scramble_addr`, making this file part of both initialization and asynchronous error-processing paths. `gaudi2_write_rr_to_all_lbw_rtrs()` is also used outside this file by Gaudi2 reset logic to temporarily program LBW deny ranges.

Build integration comes through `gaudi2/Makefile`, which includes `gaudi2/gaudi2_security.o` in `HL_GAUDI2_FILES`, and the parent HabanaLabs Makefile folds that list into the `habanalabs` kernel object.

## Risks and edge cases

The largest risk is table drift. Most behavior is encoded in long static register lists; a missing sensitive register in a protected block can expose control state, while a missing user-required register can break command submission, networking, DMA, TPC, MME, or rotator programming. Generated register-name changes are especially risky because helpers fail only when a listed register cannot be mapped into a listed protection block.

Return-code accumulation uses `rc |= ...` across many initialization calls. This preserves a non-zero failure but loses the first precise error code when multiple failures occur. Some helper paths in common security code also historically return `0` after range unsecure calls even if an internal call was not checked, so table validation matters.

Range-register encoding is address-bit sensitive. LBW short ranges use bits `[26:12]`, LBW long ranges use `[26:0]`, HBW short ranges use split bits `[47:44]` and `[43:12]`, and HBW long ranges use `[63:44]` and `[43:12]`. Off-by-one max addresses, non-aligned endpoints, or using the wrong short/long type can overblock or underblock memory. MMU ranges depend on address scrambling and on `dram_user_base_address` being initialized before this code runs.

Security-enabled firmware paths intentionally skip some host-side programming. Any later change to firmware ownership of CPU/PSOC/PLL/thermal security must be reflected here, or the driver may leave a block unprotected/unacknowledged or attempt forbidden register access.

There are a few specialized hardware quirks embedded in comments and constants, such as NIC QPC 64-bit bulk writes requiring adjacent reserved words and `SPECIAL_GLBL_SPARE` to be unprotected. These exceptions are easy to break during mechanical table cleanup.

`gaudi2_ack_protection_bits_errors()` mirrors initialization but is not identical: it acknowledges HBM protection blocks even though HBM does not appear in `gaudi2_init_protection_bits()`, and the sync-manager MSTR IF list is acknowledged twice around the GLBL acknowledgement. Reviewers should treat the ack list as an independent error-scan policy, not a generated inverse of initialization.

## Test signals

Useful static checks include compiling the HabanaLabs module, ensuring every `mm*` register listed in an unsecure array maps into one of that table's base blocks, and validating short/long range-register indices against `NUM_SHORT_*_RR` and `NUM_LONG_*_RR`. A focused unit-style check around common `hl_unsecure_register*()` helpers can catch out-of-block offsets and range loops.

Runtime signals include successful device probe and compute reset on Gaudi2, absence of unexpected protection-bit errors during command submission, and expected security violations when deliberately touching protected APB or external-write addresses. Logs from `gaudi2_pb_print_security_errors()` should decode cause bits and clear after `gaudi2_ack_protection_bits_errors()` runs.

Regression coverage should exercise both `fw_security_enabled` true and false paths, enabled-mask combinations for disabled HMMU/HIF/EDMA/XBAR/NIC/HBM instances, TPC tensor/SRF/lock-value register programming, NIC QPC WQE doorbell programming, and MMU reserved-DRAM blocking with scrambled addresses.
