# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_mem_maps.c

## Purpose
This file provides mock DSP memory maps and XM algorithm-header helpers for Cirrus DSP KUnit tests. It models ADSP2 16-bit, ADSP2 32-bit, and HALO address layouts closely enough for firmware loading, coefficient patching, packed-memory math, and algorithm discovery tests.

## Important APIs, Types, And Functions
It exports region arrays and size arrays for HALO, ADSP2 32-bit, and ADSP2 16-bit DSPs. Utility functions include `cs_dsp_mock_count_regions()`, `cs_dsp_mock_size_of_region()`, `cs_dsp_mock_base_addr_for_mem()`, register-block length conversion helpers, `cs_dsp_mock_has_zm()`, packed-to-unpacked mapping, and packed-register count conversion.

The XM-header builder path uses static template headers for HALO and ADSP2, `cs_dsp_create_mock_xm_header()`, `cs_dsp_mock_xm_header_write_to_regmap()`, `cs_dsp_mock_xm_header_get_alg_base_in_words()`, `cs_dsp_mock_xm_header_get_fw_version()`, and `cs_dsp_mock_xm_header_drop_from_regmap_cache()`. Internal add functions populate algorithm descriptor lists and write the `0xbedead` terminator.

## Control Flow, State, And Persistence
Most helpers are pure calculations against `struct cs_dsp_test` and the configured `dsp->mem` pointer. XM-header builders allocate KUnit-owned blob data, copy a template for the target DSP type, append algorithm entries with optional auto-allocation of base addresses, and later write the blob into the mock regmap. Cache-drop helpers remove expected registers so tests can detect unexpected dirty writes.

## Dependencies And Integration Points
The file depends on KUnit assertions, regmap access, WMFW structures, and public cs_dsp test utility types. It exports namespace `FW_CS_DSP_KUNIT_TEST_UTILS` and is linked into `cs_dsp_test_utils`.

## Risks And Test Signals
Risks are arithmetic mismatches between mock and production `region_to_reg()` logic, address-unit confusion between ADSP2 16-bit register indexes and HALO byte addresses, and auto-allocation off-by-one behavior. Tests should validate base lookup, block sizes for each memory type, packed/unpacked conversion, algorithm header write/drop/readback, firmware version extraction, and expected failures for unsupported DSP or memory types.
