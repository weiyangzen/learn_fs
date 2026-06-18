<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json

Purpose: Registry v2 global service config optimized for CI E2E.

APIs and control flow: Enables file cache, file credential mode, ioEngine 0, delayed background download, disabled P2P, audit logging, and `registryFsVersion` v2.

State and persistence: Directs logs to `/var/log/overlaybd.log`, audit logs to `/var/log/overlaybd-audit.log`, cache to `/opt/overlaybd/registry_cache`, and credentials to `/opt/overlaybd/cred.json`.

Dependencies and integration: Copied to `/etc/overlaybd/overlaybd.json` in CI before starting `overlaybd-tcmu`.

Risks and test signals: Download delay is 600 seconds, so CI mostly validates open/mount and not full background download completion. Config parsing and daemon startup validate shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-registryv2.json -->
