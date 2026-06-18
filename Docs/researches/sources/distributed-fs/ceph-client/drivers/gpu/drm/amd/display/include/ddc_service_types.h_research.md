# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/ddc_service_types.h

Purpose: defines DDC/AUX service result and capability types plus DisplayPort branch/device IDs and PSR-related DPCD offsets used by AMD display link detection.

Important APIs and control flow: constants identify known DP branch/dongle device IDs, branch revisions, forced PSR-SU capability offset, and PSR active-vtotal registers. `enum ddc_result` reports DDC transaction outcomes, including busy, timeout, protocol/NACK, incomplete, invalid operation, overflow, and HPD disconnect. `enum ddc_service_type` distinguishes connector and MST service instances. `display_sink_capability` captures dongle type, downstream sink count validity, audio/video latencies, HDMI pixel/deep-color caps, spread-spectrum support, DP lane/rate/spread fields, DP-HDMI 3D conversion, eDP sink cap validity, transaction type, and signal. `av_sync_data` stores latency bytes read from DPCD.

State and persistence behavior: no direct state. These structures persist as cached sink capability data in link/DDC objects elsewhere.

Dependencies and integration points: relies on display enums for dongle, color depth, DDC transaction, and signal types. Integrated with I2C-over-AUX/DDC probing, MST branch handling, dongle capability parsing, PSR-SU forcing, and AV sync handling.

Risks and test signals: risks include typo-preserved result names, stale vendor/device IDs, unit mismatch for latency fields, misspelled `dp_link_spead`, and capability caches becoming invalid across hotplug. Test signals include DDC failure mapping, known dongle detection, MST downstream count handling, eDP cap caching, PSR active-vtotal register access, and AV sync values parsed from DPCD bytes.
