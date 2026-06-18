# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_bin.c

## Purpose
This file builds synthetic WMDR/bin coefficient firmware images for Cirrus DSP KUnit tests. It lets tests construct valid or intentionally malformed coefficient payloads without external firmware files.

## Important APIs, Types, And Functions
`struct cs_dsp_mock_bin_builder` tracks the KUnit test context, vmalloc buffer, write cursor, and bytes used. `cs_dsp_mock_bin_init()` creates the builder, writes a `WMDR` header with requested format and firmware version, and registers buffer cleanup. `cs_dsp_mock_bin_get_firmware()` wraps the buffer in a KUnit-allocated `struct firmware`.

Block-building APIs are `cs_dsp_mock_bin_add_raw_block()`, `cs_dsp_mock_bin_add_info()`, `cs_dsp_mock_bin_add_name()`, `cs_dsp_mock_bin_add_patch()`, and `cs_dsp_mock_bin_add_patch_off32()`. They populate `struct wmfw_coeff_item` fields, enforce payload alignment for patch helpers, pad text blocks to 4-byte boundaries, and support long-offset block types by setting the extended type bits.

## Control Flow, State, And Persistence
The builder appends blocks sequentially into a 32 KiB vmalloc buffer. KUnit assertions guard buffer overflow and invalid version widths. The produced `struct firmware` points directly at builder-owned memory, so it remains valid for the test lifetime through KUnit cleanup actions.

## Dependencies And Integration Points
The file depends on KUnit resource management, `linux/firmware.h`, public cs_dsp test utilities, and WMFW/WMDR structure definitions. It exports helper symbols in namespace `FW_CS_DSP_KUNIT_TEST_UTILS`.

## Risks And Test Signals
Risks include builder pointer arithmetic on void pointers, mismatch between helper `type` arguments and parser expectations, and text helper currently routing both name and info through an info block path. Test signals are KUnit cases that load name/info blocks, normal and long-offset patches, payload alignment failures, and malformed raw blocks for parser error coverage.
