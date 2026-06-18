# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/iwl-spectrum.h

## Purpose
`iwl-spectrum.h` defines small IEEE 802.11 spectrum measurement report and request structures used by iwlegacy for measurement notifications and reports.

## Important APIs, Types, and Constants
- Basic report map bits: `IEEE80211_BASIC_MAP_BSS`, `OFDM`, `UNIDENTIFIED`, `RADAR`, and `UNMEASURED`.
- Measurement mode bits: `IEEE80211_MEASUREMENT_ENABLE`, `REQUEST`, and `REPORT`.
- Report type constants: `IEEE80211_REPORT_BASIC`, `CCA`, and `RPI`.
- Packed wire structures: `struct ieee80211_basic_report` and `struct ieee80211_measurement_params`.

## Control Flow and Integration
The header has no executable logic. The packed structures are used by code that parses or builds firmware/mac80211 spectrum measurement data. `struct il_priv` caches a spectrum measurement notification and status in `common.h`; handlers declared there consume these formats.

## State and Persistence Behavior
No state is stored in the header. Instances of the packed structures represent transient measurement request/report payloads with little-endian time and duration fields.

## Dependencies and Integration Points
It depends on Linux integer/endian types included before use. It integrates with iwlegacy command/notification handlers and 802.11h/spectrum-management behavior.

## Risks and Edge Cases
Because the structures are packed wire formats, alignment and endian handling matter. Reserved bits are not masked by helper functions in this header, so callers must validate mode and map fields themselves.

## Test Signals
Validation should cover measurement notification parsing, report generation, endian conversion on big-endian builds, and radar/unmeasured flag propagation into any mac80211-visible report path.
