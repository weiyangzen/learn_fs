# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hdmi_types.h

## Purpose
`dc_hdmi_types.h` defines HDMI and DP-HDMI adapter register constants and SCDC byte overlays used by HDMI 2.0 link management, scrambling, clock detection, error counters, and DP dual-mode adapter probing.

## Important APIs And Types
Constants define DP adapter type-2 register offsets, ID, and TMDS clock limits. `struct dp_hdmi_dongle_signature_data` models the `"DP-HDMI ADAPTOR"` signature plus EOT byte. SCDC constants define address `0x54` and offsets for sink/source version, update flags, TMDS config, scrambler status, status flags, character error detection, test config, manufacturer OUI, and device ID.

The unions `hdmi_scdc_update_read_data`, `hdmi_scdc_status_flags_data`, `hdmi_scdc_ced_data`, `hdmi_scdc_manufacturer_OUI_data`, and `hdmi_scdc_device_id_data` overlay SCDC payload bytes with named fields.

## Control Flow And State
This is a declarative header. Runtime state is read from or written to HDMI SCDC registers by I2C/DDC helpers elsewhere. Error counters and lock bits are transient sink status data.

## Dependencies And Integration Points
It includes `os_types.h`. Integration points include HDMI 2.0 scrambling setup, TMDS clock validation, DP++ dongle detection, SCDC status polling, and HDMI diagnostics/error reporting.

## Risks
Bitfield overlays must match HDMI SCDC byte layout exactly. TMDS clock constants mix MHz and kHz naming, so callers must use the unit indicated by each macro. The CED union maps an 11-byte block with several partial-width fields; checksum and valid-bit interpretation should be validated against the spec.

## Test Signals
HDMI 2.0 4K60 modes requiring SCDC scrambling, DP-HDMI adapter detection, SCDC clock/channel lock polling, CED counter reads, and malformed/absent SCDC sink tests are the key signals.
