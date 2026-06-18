# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_ssr.c

Purpose: rpmsg client for Qualcomm GLINK subsystem restart cleanup. It lets remoteproc stop paths notify a remote GLINK SSR service and wait briefly for a cleanup acknowledgement before restart proceeds.

Important APIs, types, and functions: `struct do_cleanup_msg` and `struct cleanup_done_msg` encode the GLINK SSR protocol. `struct glink_ssr` stores the rpmsg endpoint, notifier block, sequence number, and completion. `qcom_glink_ssr_notify()` is an exported symbol that calls the global blocking notifier chain. `qcom_glink_ssr_callback()` validates `cleanup_done` responses, and `qcom_glink_ssr_notifier_call()` sends `do_cleanup` requests.

Control flow: when an rpmsg device named `glink_ssr` is probed, the driver initializes a completion, records `rpdev->ept`, and registers a notifier. A remoteproc user calls `qcom_glink_ssr_notify(ssr_name)`, which invokes every registered instance. Each instance increments its sequence number, fills a cleanup request with version 0, command 0, name length, and a bounded subsystem name, sends it with `rpmsg_send()`, then waits up to one second for `qcom_glink_ssr_callback()` to receive matching response 1 and complete the waiter. Remove unregisters the notifier.

State and persistence: only in-memory sequence number and completion state are kept. There is no persisted cleanup state; failures are logged and notifier returns `NOTIFY_DONE` regardless, so cleanup is best-effort.

Dependencies and integration points: integrates the rpmsg bus, Qualcomm GLINK service name `glink_ssr`, Linux notifier chains, and remoteproc Qualcomm restart code via exported `qcom_glink_ssr_notify()`.

Risks: `name_len` uses `strlen(ssr_name)` while `name` is truncated to 32 bytes by `strscpy()`, so a long input can advertise a length larger than the transmitted fixed buffer. Notifications serialize through the blocking notifier call chain, but per-instance `seq_num` is not otherwise locked. A timeout does not fail the notifier, so callers must tolerate incomplete remote cleanup.

Test signals: bind an rpmsg channel named `glink_ssr`, call `qcom_glink_ssr_notify()` with normal and long names, validate cleanup messages on the remote side, inject wrong version/response/sequence replies, and confirm timeout logs when no response arrives.
