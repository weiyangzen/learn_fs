# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.c

## Purpose
`link_ddc.c` implements generic display transport operations for DDC I2C, I2C-over-AUX, native AUX, fixed-VS retimer AUX access, and HDMI SCDC reads/writes. The file is intentionally protocol-level plumbing: it creates/destroys `ddc_service`, chunks I2C/AUX payloads, applies known dongle timing workarounds, dispatches raw AUX through DMUB or legacy DCE AUX, and exposes helpers used by DP capability detection, link training, HDMI scrambling setup, and low-level DPCD access.

## Important APIs, Types, And Functions
- `struct i2c_payloads` wraps a DAL `vector` of `struct i2c_payload`; `i2c_payloads_create/add/get/get_count/destroy` allocate, chunk, and release I2C command payloads.
- `link_create_ddc_service()` allocates a `ddc_service`, queries BIOS I2C GPIO data unless this is a DPIA link, and creates a GPIO DDC pin when available.
- `link_destroy_ddc_service()` tears down the GPIO DDC pin and frees the service.
- `set_ddc_transaction_type()`, `link_is_in_aux_transaction_mode()`, and `set_dongle_type()` update per-service transport policy.
- `link_get_aux_defer_delay()` applies generic and dongle-specific AUX defer delays; `defer_delay_converter_wa()` handles branch IDs/names for DP-VGA and DP-DVI converters.
- `link_query_ddc_data()` is the main read/write entry point. It chooses AUX payloads for AUX transaction modes and I2C command submission otherwise.
- `link_aux_transfer_raw()` dispatches to `dce_aux_transfer_dmub_raw()` when DMUB AUX is enabled or no DDC pin exists, otherwise to `dce_aux_transfer_raw()`.
- `link_aux_transfer_with_retries_no_mutex()` wraps `dce_aux_transfer_with_retries()` and is used for callers that already handle locking.
- `try_to_configure_aux_timeout()` programs AUX timeout through the DDC engine and applies the DCN 3.1 fixed-VS timeout workaround.
- `link_get_fixed_vs_pe_retimer_write_address()`, `link_get_fixed_vs_pe_retimer_read_address()`, `link_configure_fixed_vs_pe_retimer()`, and `link_query_fixed_vs_pe_retimer()` target vendor LTTPR/retimer address windows derived from `phy_repeater_cnt`.
- `write_scdc_data()` and `read_scdc_data()` access HDMI SCDC registers for source version, TMDS scrambling, and status reads.

## Control Flow
Construction begins from `ddc_service_construct()`: it records `link` and `ctx`, skips pin creation for DPIA or failed BIOS I2C info, otherwise builds a GPIO DDC object with BIOS line/engine metadata. DDC queries flow through `link_query_ddc_data()`. In AUX modes, it creates an `aux_payload`, writes the optional offset/address phase with `mot` held when a read follows, and reads back via `submit_aux_command()`, which slices transfers into `DEFAULT_AUX_MAX_DATA_SIZE` chunks. In native I2C mode, it builds write/read payload vectors in `EDID_SEGMENT_SIZE` chunks and sends one `i2c_command` through `dm_helpers_submit_i2c()`.

Fixed-VS retimer access calculates a vendor DPCD base from the encoded LTTPR count, then issues native AUX reads/writes at that address. SCDC setup first checks local sink panel patches and SCDC presence, reads sink version, optionally writes source version, then writes `TMDS_CONFIG` according to pixel clock and low-rate scrambling policy.

## State And Persistence
The file mutates persistent link/service state:
- `ddc_service->ddc_pin`, `ctx`, `link`, `transaction_type`, `dongle_type`, `flags`, and `wa`.
- `link->wa_flags.dp_keep_receiver_powered` is indirectly influenced by capability code that depends on DDC/AUX behavior.
- `link->dpcd_caps` fields drive defer delay and retimer address selection.
- `link->dpia` links are represented by a `ddc_service` with no GPIO DDC pin, routing raw AUX through DMUB.
- HDMI SCDC writes persist in the sink until the sink or link state changes.

## Dependencies And Integration Points
This file depends on DAL vectors, DCE AUX, GPIO/DDC services, BIOS I2C info, DPCD helpers, DM helper I2C submission, Atom firmware IDs, and HDMI SCDC constants. It is called by DP capability retrieval, DP training/DPCD helpers, HDMI link setup, and fixed-VS retimer code. `link_ddc.h` explicitly warns that `link_aux_transfer_with_retries_no_mutex()` requires external DM-side mutexing.

## Risks And Edge Cases
- `link_get_fixed_vs_pe_retimer_write_address()` returns a base address even when `phy_repeater_cnt` is invalid (`offset == 0xFF`), so callers depend on capability validation/workarounds.
- `try_to_configure_aux_timeout()` assumes a PHY endpoint before indexing `ddc_pin`; the early endpoint check prevents non-PHY access, but a malformed PHY link with no pin would be risky.
- AUX chunking changes `mot` only on the final chunk; regressions here can break EDID/I2C-over-AUX compliance.
- Converter delay workarounds compare branch names using the destination array size; mismatched string/padding behavior could miss a workaround.
- SCDC writes ignore return status, which is typical for best-effort HDMI setup but makes failures visible only through downstream behavior.

## Test Signals
Useful signals include EDID reads over I2C and I2C-over-AUX, AUX defer/retry behavior with DP-VGA/DVI/HDMI active converters, fixed-VS LTTPR retimer reads/writes, HDMI 2.0 SCDC scrambling at below/above 340 MHz, DPIA links with no GPIO DDC pin, and AUX timeout programming on DCN 3.1 fixed-VS platforms.
