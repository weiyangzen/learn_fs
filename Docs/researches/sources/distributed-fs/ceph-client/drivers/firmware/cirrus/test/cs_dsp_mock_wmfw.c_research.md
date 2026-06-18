# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_wmfw.c

## Purpose
This file builds synthetic WMFW firmware images for Cirrus DSP KUnit tests. It supports firmware headers, info/data blocks, and algorithm coefficient metadata blocks across WMFW format versions so parser tests can exercise both valid and malformed firmware without external files.

## Important APIs, Types, And Functions
`struct cs_dsp_mock_wmfw_builder` tracks KUnit context, selected format version, vmalloc buffer, write cursor, bytes used, current algorithm block header, and coefficient count. `cs_dsp_mock_wmfw_init()` creates the builder, chooses a default format version when negative, allocates a 128 KiB buffer, and initializes ADSP2/HALO headers via `cs_dsp_init_adsp2_halo_wmfw()`. `cs_dsp_mock_wmfw_get_firmware()` returns a `struct firmware` wrapper.

Block APIs include `cs_dsp_mock_wmfw_add_raw_block()`, `cs_dsp_mock_wmfw_add_info()`, `cs_dsp_mock_wmfw_add_data_block()`, `cs_dsp_mock_wmfw_start_alg_info_block()`, `cs_dsp_mock_wmfw_add_coeff_desc()`, and `cs_dsp_mock_wmfw_end_alg_info_block()`. They encode v1 fixed-string algorithm data or v2/v3 variable-length string formats, count coefficients, and fill region lengths.

## Control Flow, State, And Persistence
The builder appends data sequentially. Algorithm-info construction is stateful: `start_alg_info_block()` reserves and writes the algorithm header, repeated `add_coeff_desc()` calls append descriptors and increment `num_coeffs`, and `end_alg_info_block()` backfills region length and coefficient count. KUnit cleanup owns the vmalloc buffer lifetime.

## Dependencies And Integration Points
The file depends on KUnit resources, WMFW structure definitions, mock memory-map helpers for sizes, `linux/firmware.h`, and exported test utility namespace `FW_CS_DSP_KUNIT_TEST_UTILS`. It is used by WMFW load and error tests for `cs_dsp_load()` and coefficient-control parsing.

## Risks And Test Signals
Risks include encoding mismatches with production parser expectations, format-version-specific string padding mistakes, unchecked NULL optional strings in some descriptor paths, and buffer size assumptions. Test signals include format v1/v2/v3 algorithm blocks, zero/long strings, multiple coefficients, data blocks for each memory type, header size validation, and malformed lengths/strings used by error-path suites.
