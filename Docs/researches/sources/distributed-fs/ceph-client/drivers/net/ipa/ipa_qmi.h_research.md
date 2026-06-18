# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_qmi.h

Purpose: defines QMI handshake state embedded in `struct ipa` and declares setup/teardown functions.

Important APIs/types: `struct ipa_qmi` contains the QMI client handle, server handle, modem QRTR socket address, init-driver work item, and flags for `initial_boot`, `uc_ready`, `modem_ready`, `indication_requested`, and `indication_sent`. `ipa_qmi_setup()` starts the QMI service/lookup; `ipa_qmi_teardown()` stops them.

Control flow: called at the end of `ipa_setup()` after AP command/exception endpoints and local memory/table setup are ready. On modem crash/shutdown, QMI core bye handling resets the state and a new handshake begins when the modem service returns.

State/persistence: readiness flags persist across messages; `initial_boot` is cleared only after the first complete handshake. QMI handles persist while IPA setup is active.

Dependencies/integration: includes Linux QMI and workqueue support; implementation depends on IPA memory/endpoints, modem start, and QMI message definitions.

Risks: the header documents that the modem must not touch IPA hardware until handshake completion; callers should preserve setup ordering so the advertised memory and endpoint IDs are valid before QMI starts.

Test signals: setup creates both QMI handles, teardown cancels work safely, and SSR cycles reset only per-boot flags while preserving UC/initial boot semantics as intended.
