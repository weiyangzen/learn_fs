# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_rw.c

## Purpose
This file is a KUnit test suite for Cirrus Logic `cs_dsp` coefficient control read/write behavior. It validates that controls discovered from WMFW algorithm metadata are backed by the correct DSP memory addresses, respect volatile and access flags, use cached values when appropriate, reject invalid ranges, and behave consistently across ADSP2 16-bit, ADSP2 32-bit, and HALO DSP memory maps.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` stores the mock XM header, WMFW builder, and WMFW version. `struct cs_dsp_ctl_rw_test_param` drives parameterized cases with memory type, algorithm id, DSP-word offset, byte length, control type, and flags. The helper tables define four algorithms with distinct XM/YM/ZM windows; `_find_alg_entry()` and `_get_alg_mem_base_words()` resolve expected memory bases. `_create_dummy_wmfw()` creates a builder and inserts the XM header block.

The tests exercise `cs_dsp_power_up()`, `cs_dsp_run()`, `cs_dsp_stop()`, `cs_dsp_power_down()`, `cs_dsp_coeff_lock_and_read_ctrl()`, `cs_dsp_coeff_lock_and_write_ctrl()`, and regmap raw I/O through the mock regmap.

## Control Flow
Each case creates a coefficient descriptor inside a WMFW algorithm info block, powers up a mock DSP, fetches the first `struct cs_dsp_coeff_ctl` from `dsp->ctl_list`, and then performs the targeted read or write. Running-firmware cases access live regmap-backed memory. Cached-control cases start then stop the DSP. Stale volatile cases load or run a different firmware and verify the old control fails. Bounds and flag cases verify no register writes happen after rejected operations.

Suite definitions cover HALO WMFW v3 and ADSP2 16-bit/32-bit WMFW v1/v2. Parameter arrays vary lengths, offsets, XM/YM/ZM memory, algorithm IDs, and combinations of readable, writeable, volatile, and sys flags.

## State And Persistence Behavior
State is KUnit-scoped: device refs, DSP removal, and stop actions are registered as cleanup actions. The meaningful state under test is `dsp->ctl_list`, DSP running/powered state, per-control cache data, and mock regmap dirty state. Nonvolatile controls retain cached data after stop; volatile controls require the same firmware to be running.

## Dependencies And Integration Points
The file depends on KUnit, regmap, Cirrus `cs_dsp` and WMFW headers, and `cs_dsp_test_utils.h`. It integrates with real `cs_dsp` initialization and firmware load paths while using mock region tables and mock regmap utilities.

## Risks And Edge Cases
Risk coverage includes stale firmware ownership, volatile access after stop/power-down, read-only/write-only semantics, out-of-bounds offsets, length overflow, partial reads/writes, cache/live divergence, and unexpected writes. The suite is slow and depends on correctness of mock address calculation.

## Test Signals
Passing tests indicate coefficient controls resolve to correct DSP memory, enforce bounds and flags, preserve nonvolatile cache semantics, reject stale volatile operations, and avoid dirtying registers on failure.
