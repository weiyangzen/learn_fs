# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_resource.h

Purpose: exposes the resource configuration entry point used by top-level IPA config.

Important APIs: `ipa_resource_config(struct ipa *ipa, const struct ipa_resource_data *data)` validates and programs source/destination resource group limits. The comment says there is no deconfig path because hardware defaults or later reset cover cleanup.

Control flow: called once during `ipa_config()` after endpoint/table configuration and before modem notifier setup.

State/persistence: no header-visible state. Hardware programmed limits persist after the function returns.

Dependencies/integration: forward-declares `struct ipa` and `struct ipa_resource_data` from data tables.

Risks: the documented return text says true/false, but the function actually returns `0` or a negative errno. Callers correctly use errno semantics.

Test signals: compile-time callers treat return as errno, probe fails on invalid resource data, and supported data tables configure without warnings.
