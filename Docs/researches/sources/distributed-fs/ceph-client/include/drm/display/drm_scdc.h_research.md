# sources/distributed-fs/ceph-client/include/drm/display/drm_scdc.h

Purpose: HDMI 2.x Status and Control Data Channel register definitions for scrambling, TMDS bit clock ratio, read requests, lock/status flags, error counters, and sink identification.

Important APIs/types/functions: no functions. Constants include SCDC version registers, update flags, `SCDC_TMDS_CONFIG`, scrambler status, read request config, channel lock/clock detect bits, CED counters, test controls, manufacturer OUI, device ID, revisions, and manufacturer-specific size.

Control flow: HDMI drivers use these offsets over DDC/I2C to enable scrambling, set 1/40 clock ratio, read lock/error status, and identify sink capabilities.

State and persistence: no header state. SCDC registers are sink-side runtime state and reset on hotplug, power loss, or mode changes.

Dependencies and integration points: standalone constants used by `drm_scdc_helper.h`, HDMI bridge/encoder mode-setting, and DDC/I2C adapters.

Risks and test signals: scrambling without support, clock-ratio mismatch, stale status, counter interpretation, and sink quirks are risks. Test HDMI 2.0 high TMDS modes, scrambling status, clock ratio set/clear, channel locks, CED counters, and hotplug reset.
