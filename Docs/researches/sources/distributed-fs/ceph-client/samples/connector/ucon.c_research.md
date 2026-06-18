# sources/distributed-fs/ceph-client/samples/connector/ucon.c

Purpose: user-space netlink connector utility for the `cn_test` module.

Important APIs/functions: opens `PF_NETLINK`/`NETLINK_CONNECTOR`, binds to all connector groups, builds `struct nlmsghdr` plus `struct cn_msg` in `netlink_send`, uses `poll`, `recv`, and `send`, and prints received `NLMSG_DONE` messages.

Control flow: parses `-h` and `-s`; optional output file is opened append/update. Default mode binds and waits in a poll loop, printing timestamps and connector IDs for received messages. Send mode constructs a zero-length `cn_msg` for `CN_NETLINK_USERS + 3` / `0x456` and sends 10 batches of 1000 messages.

State and persistence: process-local sequence number and optional output file. No durable state except appended logs.

Dependencies and integration: requires connector UAPI headers and the `cn_test` module using matching IDs. Uses netlink protocol number 11.

Risks: fixed stack buffers assume small messages; the send path does not bound arbitrary future message lengths. Binding to `nl_groups = -1` subscribes broadly. File-open error message references `argv[1]` rather than the actual output argument.

Test signals: run `ucon` while `cn_test.ko` is loaded to see periodic counters; run `ucon -s` and check kernel log callback lines.
