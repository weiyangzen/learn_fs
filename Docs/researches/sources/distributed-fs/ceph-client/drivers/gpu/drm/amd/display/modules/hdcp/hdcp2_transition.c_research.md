# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_transition.c

Purpose: implements HDCP 2.2 transition decisions for HDMI/DVI and DisplayPort. It interprets the execution input structure, controls timers, retries, and fallback policy, and decides when authentication is complete.

Important APIs: `mod_hdcp_hdcp2_transition()` handles `H2_*` states; `mod_hdcp_hdcp2_dp_transition()` handles `D2_*` states. Both use `struct mod_hdcp_transition_input_hdcp2`, `struct mod_hdcp_event_context`, and `struct mod_hdcp_output`.

Control flow: both paths check receiver capability, create PSP sessions, prepare/write AKE Init, validate AKE cert, select stored or no-stored KM, validate H', run locality check, exchange KS/EKS, and either authenticate direct receivers or run repeater receiver-id-list and stream-management states. HDMI polls several messages with callbacks and watchdogs; DP has explicit content-stream-type signaling before encryption and DP link-integrity checks during authentication.

State and persistence: state is carried in `hdcp->state.id`, `stay_count`, `hdcp->auth.count.stream_management_retry_count`, `conn->is_km_stored`, `conn->is_repeater`, and link adjustment flags. The transition can disable HDCP2 capability, force no stored KM after H' validation failure, switch from firmware to software locality check, or force Type 0 on repeated DP Type 1 link-integrity failures.

Dependencies and integration: depends on `hdcp2_execution.c` to set each input field and on top-level HDCP scheduling to honor callback/watchdog requests. It is tightly coupled to HDCP 2.2 CTS timing, including 100 ms, 200 ms, 1000 ms, 2000 ms, and 3000 ms watchdogs/callbacks.

Risks: retry counters and timer durations are security and compatibility boundaries. HDMI repeater flows can be interrupted by CPIRQ receiver-id-ready events at multiple states. DP content type and MST stream-encryption failures can require fallback to Type 0, so errors can look like policy rather than transport failures.

Test signals: test invalid cert/H'/L'/M'/V', revoked receiver IDs, stored-KM fallback, firmware locality fallback, receiver-id-list timeout, stream-ready retry limit, DP CPIRQ arrival in authenticated states, direct versus repeater, and Type 1 to Type 0 fallback.
