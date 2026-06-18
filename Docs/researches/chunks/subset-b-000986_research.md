# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 1-4331

## Scope

This chunk is the opening slice of the auto-generated Gaudi2 block-map header used by the Habana Labs Linux accelerator driver. It covers the file preamble, include guard, and the first 4,317 `#define` register-window macros. The visible range describes tensor-processing-core (TPC) and embedded logic (EML) block windows from `DCORE0_TPC0` through all of `DCORE2_TPC4`, then stops inside the beginning of `DCORE2_TPC5` after `DCORE2_TPC5_EML_TPC_CFG_KERNEL_TENSOR_2_MAX_OFFSET`.

The code is not Ceph distributed filesystem logic despite living in a Ceph-client source snapshot. It is ASIC register-address metadata for the upstream-style Linux `habanalabs` accelerator driver.

## Purpose

The header gives driver C code symbolic names for Gaudi2 MMIO block base addresses, maximum offsets, and section spans. In this chunk, every hardware window follows a generated triplet pattern:

- `mm..._BASE`: an unsigned 64-bit MMIO base address, written with an `ull` suffix.
- `..._MAX_OFFSET`: the register-window size or legal offset limit for that block.
- `..._SECTION`: the generated span to the next related block or section boundary.

The purpose is to keep low-level driver code from hard-coding numeric offsets when programming, dumping, protecting, or validating Gaudi2 TPC-related hardware blocks. The constants define the address layout for TPC ROM tables, embedded trace/debug blocks, queue-manager ARC memories, TPC configuration blocks, tensor descriptor regions, sync objects, queue-manager apertures, AXUSER attributes, debug windows, clock-gating controls, and common CS windows across DCORE instances.

## Important APIs, Types, And Functions

This chunk contains no functions, structs, enums, inline helpers, or executable APIs. Its interface is the C preprocessor symbol set exported by `gaudi2_blocks_linux_driver.h`.

The visible file-level wrapper is:

- `GAUDI2_BLOCKS_LINUX_DRIVER_H_`: include guard that prevents duplicate macro definitions in a single translation unit.

The important macro families are:

- `mmDCORE*_TPC*_ROM_TABLE_BASE`, plus matching max offset and section macros, for 4 KiB ROM-table windows at the start of each TPC aperture.
- `mmDCORE*_TPC*_EML_SPMU_BASE`, `EML_ETF`, `EML_STM`, `EML_CTI`, `EML_FUNNEL`, and `EML_BUSMON_0..3`, which define embedded monitoring, tracing, cross-trigger, funnel, and bus-monitor windows.
- `mmDCORE*_TPC*_QM_ARC_RTT_BASE`, with `MAX_OFFSET 0x1400` and a larger `SECTION 0x35000`, for the TPC queue-manager ARC RTT area.
- `mmDCORE*_TPC*_EML_CFG_BASE` and `EML_CFG_SPECIAL_BASE`, for EML configuration and special-register windows.
- `mmDCORE*_TPC*_EML_TPC_CFG_BASE` and the nested `KERNEL_TENSOR_0..15`, `KERNEL_SYNC_OBJECT`, `KERNEL`, `QM_TENSOR_0..15`, `QM_SYNC_OBJECT`, `QM`, `AXUSER`, and `SPECIAL` windows, which model the TPC configuration and queue-manager-visible tensor/sync/user-attribute regions.
- `mmDCORE*_TPC*_EML_QM_DCCM_BASE`, `EML_QM_ARCAUX_BASE`, and `EML_QM_ARCAUX_SPECIAL_BASE`, which describe local QM memory and ARC auxiliary register windows.
- `mmDCORE*_TPC*_EML_TPC_QM_BASE` and nested `QMAN_WR64_BASE_ADDR0..15`, `AXUSER_SECURED`, `AXUSER_NONSECURED`, `DBG_HBW`, `DBG_LBW`, `CGM`, and `SPECIAL` windows, which define queue-manager command, address, attribute, debug, and clock-gating/register-special regions.
- `mmDCORE*_TPC*_EML_CS_BASE`, the closing common/status window for each TPC block aperture.

## Address Layout And Repetition

The visible range is highly regular. Each complete TPC instance contributes 79 `mm..._BASE` macros and 158 non-`mm` companion macros for a total of 237 definitions. In lines 1-4331, the complete TPC instances are:

- `DCORE0_TPC0` through `DCORE0_TPC6`.
- `DCORE1_TPC0` through `DCORE1_TPC5`.
- `DCORE2_TPC0` through `DCORE2_TPC4`.

The assigned chunk also includes the first 33 macros of `DCORE2_TPC5`, ending in its early `EML_TPC_CFG_KERNEL_TENSOR_2` region. The full `DCORE2_TPC5` block therefore belongs partly to the next chunk and should be reconciled there by the merge lane.

Within a complete TPC instance, the base addresses step through a consistent local aperture:

- TPC aperture start: `ROM_TABLE_BASE`.
- Early 4 KiB debug/trace windows: `SPMU`, `ETF`, `STM`, `CTI`, `FUNNEL`, `BUSMON_0..3`.
- Queue-manager ARC RTT at local `0xB000`.
- EML CFG at local `0x40000`, then TPC CFG/tensor/sync/QM descriptor subwindows beginning at local `0x41000`.
- QM DCCM and ARCAUX at local `0x42000` and `0x4A000`.
- TPC QM command-manager region at local `0x4C000`, with 16 `QMAN_WR64_BASE_ADDR*` bases spaced eight bytes apart.
- Closing EML CS at the end of the TPC aperture, such as `DCORE0_TPC0_EML_CS_BASE 0x1FF000`.

Most complete TPC apertures are spaced by `0x200000`. DCORE transitions add larger section spans on the last TPC of a DCORE in this chunk, for example `DCORE0_TPC6_EML_CS_SECTION 0x201000` before `DCORE1_TPC0`, and `DCORE1_TPC5_EML_CS_SECTION 0x401000` before `DCORE2_TPC0`. These section spans are metadata for traversing the generated register block map and should not be assumed to be the same as each block's max offset.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time flow is normal header inclusion:

1. A C file includes `gaudi2_blocks_linux_driver.h`.
2. The include guard defines `GAUDI2_BLOCKS_LINUX_DRIVER_H_` the first time the header is seen.
3. The compiler/preprocessor makes the generated address constants available to subsequent code.

All runtime behavior happens in other driver files that consume these macros for MMIO reads, MMIO writes, debug dumping, register range checks, or protection programming.

## State And Persistence Behavior

This chunk does not allocate memory, mutate kernel state, persist data, or directly touch hardware. It defines constants only.

The constants represent persistent ASIC address-map knowledge: if they are wrong, every consumer compiled against this header will target wrong MMIO windows until the driver is rebuilt with corrected definitions. The hardware state itself is changed only when other code uses these addresses with MMIO helpers.

Because the file is auto-generated and marked "DO NOT EDIT BELOW," the true source of persistence is likely an internal register database or generation pipeline rather than this checked-in header alone. Manual edits to this file would be fragile and likely overwritten by regeneration.

## Dependencies And Integration Points

The direct dependency is the C preprocessor and the consumers that include this header. There are no local include directives in this slice beyond the include guard.

Primary integration points are Habana Labs Gaudi2 driver code that needs block-level register windows, including likely code paths for:

- MMIO register access through `RREG32`, `WREG32`, or equivalent helpers.
- Device bring-up and reset flows that program TPC, QM, ARC, EML, AXUSER, and debug register blocks.
- Debugfs or diagnostic register dumps that iterate over generated block ranges using base, max-offset, and section metadata.
- Security/protection logic that maps named hardware blocks to address ranges.
- Error handling paths that decode addresses back to TPC/DCORE regions.

The header sits under `drivers/accel/habanalabs/include/gaudi2/asic_reg`, so it integrates with Gaudi2-specific ASIC register headers rather than common Linux subsystem APIs.

## Risks And Edge Cases

Generated headers are brittle at the consumer boundary. A stale or incorrect base address can silently redirect an MMIO operation to the wrong hardware block, which may cause device initialization failures, misreported diagnostics, security gaps, or register writes with unintended side effects.

The repeated macro names are easy to misuse. For each block, `MAX_OFFSET` and `SECTION` are different concepts. Some `SECTION` values are much larger than max offset, especially for `QM_ARC_RTT`, `TPC_QM_SPECIAL`, and DCORE-boundary `EML_CS` entries. Code that treats section spans as safe register access limits could overrun a block's intended register window.

Several generated definitions are duplicated or alias-like within each TPC instance. For example, `EML_CFG_SPECIAL_SECTION` appears before and after `EML_TPC_CFG_KERNEL_TENSOR_0_BASE` in each complete TPC group, and `EML_TPC_CFG_BASE` shares the same base as `KERNEL_TENSOR_0`. This is probably intentional generator output, but duplicate macro names can hide drift if the generator ever emits conflicting values.

The chunk boundary cuts through `DCORE2_TPC5`. Any file-level research or generated summaries must merge this note with the next chunk before drawing conclusions about the full DCORE2 TPC5 address map.

The constants use `ull`, which is appropriate for the 64-bit-looking MMIO namespace. Consumers that store these values in narrower integer types risk truncation as addresses grow past 32-bit ranges.

## Test Signals

Useful validation signals for this chunk are mostly static or hardware-integration oriented:

- Kernel build succeeds with no macro redefinition warnings or missing symbol errors from Gaudi2 driver consumers.
- Static checks confirm every complete TPC block in this slice has the expected 79 base macros plus matching `MAX_OFFSET` and `SECTION` companions.
- Generated register-dump tooling can walk from `DCORE0_TPC0` through `DCORE2_TPC4` without overlapping ranges unexpectedly or treating section spans as max offsets.
- On Gaudi2 hardware or simulation, driver initialization can access TPC/QM/EML registers named from these macros without MMIO faults, RAZWI events, or address decode errors.
- Security and debug tests that use TPC QM, AXUSER, debug HBW/LBW, and special-register windows hit the expected DCORE/TPC instance.
- Regeneration from the source register database produces byte-for-byte identical definitions for lines 1-4331, except for known generator-version changes.
