# sources/distributed-fs/ceph-client/drivers/soc/qcom/ubwc_config.c

## Purpose

`ubwc_config.c` is a Qualcomm UBWC capability database. It maps machine-compatible strings to `struct qcom_ubwc_cfg_data` records describing encoder/decoder versions, swizzle mode, bank spreading, highest bank bit, and macrotile support for display, GPU, video, and other consumers.

## Important APIs, Types, and Functions

The file defines many static `qcom_ubwc_cfg_data` constants, including no-UBWC fallback data and per-SoC families from older MSM parts through SM8750. The sole exported API is `qcom_ubwc_config_get_data()`, which calls `of_machine_get_match_data(qcom_ubwc_configs)` and returns either a data pointer or `ERR_PTR(-EINVAL)`.

## Control Flow

There is no probe. Consumers call the exported helper at runtime. OF machine matching scans `qcom_ubwc_configs`, selects the first compatible match in the root compatible list, and returns its `.data`. The module exports the symbol for other Qualcomm drivers.

## State and Persistence Behavior

All state is immutable static data. There is no hardware programming, persistence, or allocation. Consumers interpret the returned pointer directly.

## Dependencies and Integration Points

It depends on OF machine matching and `<linux/soc/qcom/ubwc.h>` definitions. Integration points are downstream display/media/GPU/interconnect code that must use the same UBWC version and memory-layout parameters for a given SoC.

## Risks and Edge Cases

The table is policy-critical: wrong `highest_bank_bit`, swizzle, or UBWC version can produce corruption rather than a clean failure. Several entries carry TODO comments for LPDDR4 bank-bit differences, indicating board/memory-configuration sensitivity not modeled by a single SoC-compatible key. `sm8750_data` uses a literal swizzle value `6` rather than named flags. Missing machine matches return an error after logging.

## Test Signals

Unit-style tests can validate every known root compatible maps to expected data. Hardware validation should exercise display/video/GPU UBWC surfaces on each SoC/memory variant, especially entries with TODO bank-bit notes and SoCs sharing another SoC's config.
