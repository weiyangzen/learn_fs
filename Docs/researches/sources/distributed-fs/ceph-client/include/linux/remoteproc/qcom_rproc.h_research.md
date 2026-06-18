# sources/distributed-fs/ceph-client/include/linux/remoteproc/qcom_rproc.h

Purpose: this header declares Qualcomm subsystem restart notification types and notifier registration helpers used by clients interested in remoteproc power and crash transitions.

Important APIs/types/functions: `enum qcom_ssr_notify_type` describes before/after powerup and before/after shutdown events. `struct qcom_ssr_notify_data` carries subsystem `name` and whether shutdown is crash-related. APIs are `qcom_register_ssr_notifier()` and `qcom_unregister_ssr_notifier()` when `CONFIG_QCOM_RPROC_COMMON` is enabled; stubs return `NULL`/`0` otherwise.

Control flow: consumers register a notifier for a named remote subsystem. Qualcomm remoteproc common code calls notifiers around prepare/start and stop/unprepare phases, letting clients quiesce or reinitialize resources after SSR events.

State and persistence: notifier blocks and registration handles are runtime state in the Qualcomm common implementation, not in the header. The event payload is transient.

Dependencies and integration points: depends on notifier blocks and integrates with Qualcomm remoteproc drivers, subsystem restart, rpmsg clients, modem/audio/compute subsystems, and crash recovery logic.

Risks: clients must unregister before teardown and must tolerate disabled stubs. Event ordering matters: doing work in `BEFORE_SHUTDOWN` versus `AFTER_SHUTDOWN` can affect access to shared memory and clocks. Test signals include notifier registration/unregistration, crash versus orderly stop events, disabled-config builds, and client recovery after SSR.
