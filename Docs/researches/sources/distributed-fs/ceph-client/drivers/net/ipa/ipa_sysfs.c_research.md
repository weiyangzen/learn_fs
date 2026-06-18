# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.c

Purpose: defines read-only sysfs attribute groups attached to the IPA platform device for hardware version, MAP offload type, and modem endpoint IDs.

Important APIs/data: exported groups are `ipa_attribute_group`, `ipa_feature_attribute_group`, `ipa_endpoint_id_attribute_group`, and `ipa_modem_attribute_group`. Attribute show helpers render IPA version, RX/TX offload (`MAPv4` before IPA v4.5 and `MAPv5` after), endpoint IDs for AP modem RX/TX, and legacy modem endpoint paths.

Control flow: the platform driver lists these groups in `dev_groups`, so sysfs files are created during device registration. Endpoint ID visibility checks `ipa->name_map[]` and hides attributes for undefined endpoints. Show functions recover `struct ipa` from `dev_get_drvdata()`.

State/persistence: no mutable state; sysfs output reflects `ipa->version` and endpoint mappings initialized during probe.

Dependencies/integration: depends on Linux device/sysfs helpers, `ipa_version`, endpoint names, and top-level platform driver group registration.

Risks: show functions assume drvdata and endpoint mappings are valid while attributes exist. The version string returns `"0.0"` for unexpected versions, which should not happen if match data is valid.

Test signals: sysfs exposes `/version`, `/feature/rx_offload`, `/feature/tx_offload`, `/endpoint_id/modem_rx`, `/endpoint_id/modem_tx`, and legacy `/modem/*_endpoint_id` with values matching configured endpoints.
