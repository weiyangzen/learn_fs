# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_execution.c

Purpose: executes HDCP 2.2 protocol actions for the current state and records granular PASS/FAIL/PENDING inputs consumed by the transition layer. It bridges state-machine events to DDC reads/writes, PSP cryptographic preparation/validation, receiver status polling, and DP stream operations.

Important APIs: exported entry points are `mod_hdcp_hdcp2_execution()` for HDMI/DVI-style HDCP 2.2 and `mod_hdcp_hdcp2_dp_execution()` for DisplayPort. Static helpers implement each state: `send_ake_init`, `validate_ake_cert`, `read_h_prime`, `locality_check`, `exchange_ks_and_test_for_repeater`, `enable_encryption`, `verify_rx_id_list_and_send_ack`, `send_stream_management`, and `validate_stream_ready`. `process_rxstatus()` centralizes RxStatus, reauth, link-integrity, and receiver-id-list-ready handling.

Control flow: each state validates expected event types, sets `event_ctx->unexpected_event` for invalid stimuli, then calls `mod_hdcp_execute_and_set()` around lower-level operations. HDMI uses RxStatus message-size checks for AKE cert, H', pairing info, L', receiver-id list, and stream-ready availability. DP reads capability from RxCaps and uses DP-specific RxStatus bits for H', pairing, reauth, link failure, and receiver-id readiness.

State and persistence: stores received messages under `hdcp->auth.msg.hdcp2`, increments `trace->hdcp2.attempt_count`, populates `event_ctx->rx_id_list_ready`, updates `rx_id_list_size`, and records downstream device count / legacy-device flags. Locality check may sleep or use firmware atomic write-poll-read depending on link adjustment flags.

Dependencies and integration: depends on `hdcp_ddc.c` for message transport and `hdcp_psp.c` for cryptographic message generation/validation. It integrates with transition files through `struct mod_hdcp_transition_input_hdcp2`, making each state side-effect visible without embedding transition decisions here.

Risks: RxStatus parsing is protocol- and transport-specific; wrong sizes can stall authentication. `poll_l_prime_available()` sleeps in small intervals and is HDMI-only. `check_device_count()` intentionally allows one extra display for MST internal-panel behavior, so regressions can reject valid MST topologies or accept inconsistent ones.

Test signals: cover HDMI/DP capability reads, callback versus CPIRQ events, watchdog paths, stored and no-stored KM, firmware and software locality paths, repeater receiver-id list validation, stream management retry count, DP link-integrity failure, and MST stream encryption.
