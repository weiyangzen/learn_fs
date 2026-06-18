<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/smp.h

Purpose: declares Bluetooth SMP wire-format structures, opcodes, error reasons, key-distribution/authentication constants, internal LTK type helpers, and the SMP entry points used by the rest of the Bluetooth stack.

Important APIs, types, and functions: packed command structs mirror the SMP PDUs: `smp_command_hdr`, `smp_cmd_pairing`, confirm/random/fail PDUs, encryption information, identity information, signing information, security request, Secure Connections public key, DHKey check, and keypress notification. Constants define command codes through `SMP_CMD_MAX`, IO capabilities, OOB flags, distribution bits, auth bits including Secure Connections and CT2, failure reasons, and min/max encryption key sizes. Inline helpers `smp_ltk_is_sc` and `smp_ltk_sec_level` map stored `struct smp_ltk` metadata to security levels. `enum smp_key_pref` lets callers distinguish "STK is acceptable" from "prefer an LTK".

Control flow: the header does not implement protocol flow, but it defines the contract used by `smp.c` and other Bluetooth modules. Callers use `smp_conn_security` to request a security level, `smp_sufficient_security` to decide whether the current link already satisfies policy, `smp_user_confirm_reply` to feed mgmt user decisions back into the SMP state machine, and `smp_cancel_and_remove_pairing` to abort pairing while removing stored keys. Device lifecycle code calls `smp_register`, `smp_unregister`, and `smp_force_bredr`.

State and persistence: no storage is allocated here. The LTK type enum records whether stored keys are legacy STK/LTK, responder keys, P-256 Secure Connections keys, or debug P-256 keys. Those values influence persistence and security-level decisions in `smp.c`.

Dependencies and integration points: relies on Bluetooth address and HCI key types from surrounding headers included before or with it. The public prototypes connect HCI core, L2CAP, mgmt, and privacy code to SMP implementation details while keeping the PDU layout centralized.

Risks: because the structs are packed wire contracts, field order and sizes must stay exactly aligned with the Bluetooth specification. Changing enum values or auth/distribution bit masks would corrupt negotiation and stored-key semantics. The fallback inline `bt_selftest_smp` returns success when selftests are disabled, so build configurations must be explicit when crypto vector testing is required.

Test signals: compile-time users validate the API surface. Runtime signals come through SMP selftests when enabled, Bluetooth pairing/security tests, and any code that checks security-level mapping for authenticated, unauthenticated, Secure Connections, and debug LTKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/smp.h -->
