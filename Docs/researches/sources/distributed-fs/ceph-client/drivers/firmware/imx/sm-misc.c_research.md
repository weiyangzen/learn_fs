# sources/distributed-fs/ceph-client/drivers/firmware/imx/sm-misc.c

Purpose: Provides exported wrappers and debug/event integration for the i.MX SCMI MISC protocol.

Important APIs/types/functions: Exports `scmi_imx_misc_ctrl_set()` and `scmi_imx_misc_ctrl_get()`. `scmi_imx_misc_ctrl_probe()` retrieves `scmi_imx_misc_proto_ops`, registers event notifiers for `nxp,ctrl-ids`, requests notification enablement, and creates debugfs `scmi_imx/syslog`. `syslog_show()` reads firmware syslog through the protocol and dumps hex.

Control flow: Probe validates SCMI handle, prevents duplicate init, gets protocol ops/handle, parses pairs of control IDs and flags from DT, registers a dummy notifier callback for each, requests notifications, creates debugfs directory/file, and registers a devm cleanup action. Exported get/set calls defer until probe and forward to protocol ops.

State and persistence behavior: Global ops/handle and notifier block. Firmware misc control values and notification subscriptions persist in SCMI firmware for the driver lifetime.

Dependencies and integration points: Depends on SCMI core notify ops, OF properties, debugfs, seq_file, and NXP SCMI MISC protocol definitions.

Risks and test signals: If `nxp,ctrl-ids` is absent, `of_property_count_u32_elems()` can return a negative value; modulo handling should be checked. Notification callback is intentionally a no-op, so event payloads are not surfaced. Test DT parsing, odd control list rejection, notification registration failures, syslog read size, debugfs cleanup, and exported get/set before/after probe.
