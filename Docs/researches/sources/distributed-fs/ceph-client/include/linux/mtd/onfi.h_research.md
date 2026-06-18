# sources/distributed-fs/ceph-client/include/linux/mtd/onfi.h

## Purpose

Defines ONFI NAND parameter-page structures, feature addresses, timing mode bits, CRC base, and helper declarations for ONFI identification and timing conversion.

## Important APIs, Types, and Functions

Key types include ONFI parameter/timing/extended parameter structures and exported helpers for ONFI CRC, SDR/NV-DDR timing extraction, and parameter-page parsing used by raw NAND.

Source-visible symbols include structs: `struct nand_onfi_params`, `struct onfi_ext_ecc_info`, `struct onfi_ext_section`, `struct onfi_ext_param_page`, `struct onfi_ext_section sections[ONFI_EXT_SECTION_MAX];`, `struct onfi_params`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_ONFI_H`, `ONFI_VERSION_1_0`, `ONFI_VERSION_2_0`, `ONFI_VERSION_2_1`, `ONFI_VERSION_2_2`, `ONFI_VERSION_2_3`, `ONFI_VERSION_3_0`, `ONFI_VERSION_3_1`, `ONFI_VERSION_3_2`, `ONFI_VERSION_4_0`, `ONFI_FEATURE_16_BIT_BUS`, `ONFI_FEATURE_NV_DDR`, `ONFI_FEATURE_EXT_PARAM_PAGE`, `ONFI_DATA_INTERFACE_SDR`, `ONFI_DATA_INTERFACE_NVDDR`, `ONFI_DATA_INTERFACE_NVDDR2`.

## Control Flow

Raw NAND detection reads ONFI parameter pages, validates signature/CRC, extracts geometry, timing, features, optional commands, and ECC information, then builds NAND memory organization and interface timing configs.

## State and Persistence Behavior

This header models persistent ONFI parameter data and feature-register addresses. Runtime state is stored by callers in `nand_parameters` and timing config objects.

## Dependencies and Integration Points

It integrates with raw NAND identification, `nand_interface_config`, and vendor feature handling.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/bitfield.h>`.

## Risks and Edge Cases

Packed layout, endian conversion, CRC validation, and multiple-parameter-page fallback are critical. Timing mode conversion must not overdrive the controller or chip.

## Test Signals

Golden ONFI parameter pages for multiple revisions, CRC failures, timing mode conversion, feature set/get bitmaps, and extended parameter parsing.

Source read signal: 190 lines, 4999 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
