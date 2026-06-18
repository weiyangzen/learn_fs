# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.h

## Purpose
`link_ddc.h` declares the DDC/AUX/SCDC service API used by the display link layer. It provides constants for AUX defer and timeout workarounds, the EDID segment size, and the public entry points for DDC service lifecycle, I2C/AUX transactions, fixed-VS retimer access, HDMI SCDC, dongle metadata, and raw AUX transfer.

## Important APIs And Constants
- Constants: `AUX_POWER_UP_WA_DELAY`, `I2C_OVER_AUX_DEFER_WA_DELAY`, `DPVGA_DONGLE_AUX_DEFER_WA_DELAY`, `I2C_OVER_AUX_DEFER_WA_DELAY_1MS`, `LINK_AUX_DEFAULT_LTTPR_TIMEOUT_PERIOD`, `LINK_AUX_DEFAULT_TIMEOUT_PERIOD`, and `EDID_SEGMENT_SIZE`.
- Lifecycle: `link_create_ddc_service()`, `link_destroy_ddc_service()`.
- Mode/state helpers: `set_ddc_transaction_type()`, `link_get_aux_defer_delay()`, `link_is_in_aux_transaction_mode()`, `set_dongle_type()`, `get_ddc_pin()`.
- Transport helpers: `try_to_configure_aux_timeout()`, `link_query_ddc_data()`, `link_aux_transfer_with_retries_no_mutex()`, `link_aux_transfer_raw()`.
- Retimer helpers: `link_configure_fixed_vs_pe_retimer()`, `link_query_fixed_vs_pe_retimer()`, address calculators.
- HDMI helpers: `write_scdc_data()`, `read_scdc_data()`.

## Control Flow And Integration
The header is included by DP capability, DPCD, training, and HDMI setup code. It keeps the lower-level transport surface narrow: higher layers ask for DDC data or AUX transactions without embedding GPIO, BIOS, vector, or DCE AUX details. The comment on `link_aux_transfer_with_retries_no_mutex()` is an integration contract: DC-side users should usually go through DM DPCD helpers unless they already hold the required lock.

## State And Persistence
The header exposes APIs that mutate `struct ddc_service`, sink DPCD/SCDC state, DDC GPIO engine timeout settings, and `dc_link` retimer/dongle-dependent state. It does not define new structs beyond what `link_service.h` provides.

## Risks And Test Signals
Risk centers on callers respecting locking and transport mode selection. Tests should compile all users of the prototypes, exercise I2C and AUX transaction modes, validate timeout constants against training/capability paths, and confirm fixed-VS and SCDC declarations stay synchronized with `link_ddc.c`.
