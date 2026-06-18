# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.h

## Purpose

`hclge_err.h` is the public and shared definition header for HNS3 PF hardware error handling. It declares interrupt masks, status masks, descriptor limits, module/type identifiers, error logging structures, module register dump descriptors, and the functions used by `hclge_main.c` and related PF subsystems to configure and handle hardware errors.

## Important Types And Constants

The header defines minimum BD counts for MPF/PF RAS and MSI-X status queries, RAS status register addresses and masks, vector0 MSI-X masks, per-block interrupt enable and mask constants for COMMON, IGU/EGU, PPP, TM/QCN, NCSI, MAC, PPU, SSU, and RoCEE, plus descriptor and register-list sizing limits. `enum hclge_err_int_type` classifies MSI-X and RAS CE/NFE/FE categories. `enum hclge_mod_name_list` and `enum hclge_err_type_list` encode firmware module and error type IDs for all-error logs.

Core structures include `hclge_hw_blk` for configurable error blocks, `hclge_hw_error` for status-bit to message/reset mappings, `hclge_hw_module_id` and `hclge_hw_type_id` for all-error summary decoding, `hclge_sum_err_info`, `hclge_mod_err_info`, and `hclge_type_reg_err_info` for firmware log records, and `hclge_mod_reg_info` plus `hclge_mod_reg_common_msg` for follow-up DFX register queries.

## Exported APIs

The declared APIs configure MAC tunnel interrupts, NIC hardware error interrupts, and RoCEE RAS interrupts; handle all HNS hardware errors during init; locate and process occurred errors; process PCI RAS and MSI-X hardware error paths; log firmware all-error info; handle MAC tunnel interrupts; and perform VF queue-error RAS recovery.

## Control Flow And State

The header itself has no runtime control flow, but its constants determine which bits are enabled, queried, logged, cleared, or converted into reset requests by `hclge_err.c`. Its firmware record structures define the in-memory overlay used when descriptor data is decoded.

## Dependencies And Integration Points

It includes `hclge_main.h`, `hclge_debugfs.h`, and `hnae3.h`. This ties error handling to the PF device state, debug command helpers for module register dumps, and HNAE3 reset/error enums. `hclge_main.c` and AE ops use the function declarations directly.

## Risks

Because this header mirrors hardware and firmware contracts, mask mistakes can enable the wrong interrupt, fail to clear a source, or misclassify reset severity. Descriptor size constants must match command queue payload layout. Firmware all-error structures are compact and interpreted from raw `u32` buffers; field order and maximum register count are critical. Including `hclge_debugfs.h` creates a coupling from error handling to debug helper declarations.

## Test Signals

Build coverage should include sparse/endian checks and all supported device revisions. Runtime tests should validate interrupt masks against firmware documentation, all-error log decoding, RoCEE capability gating, VF fault support gating, and reset-level propagation from `hclge_hw_error` tables.
