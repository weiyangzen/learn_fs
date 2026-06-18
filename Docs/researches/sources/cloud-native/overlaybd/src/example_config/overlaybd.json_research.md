<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd.json -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd.json

Purpose: General default global config for installed OverlayBD.

APIs and control flow: Configures file registry cache, optional gzip cache enabled by default, file credentials, ioEngine 0, delayed background download, disabled P2P, disabled metrics exporter, audit logging, registryfs v2, and disabled snapshot service.

State and persistence: Uses `/opt/overlaybd/registry_cache`, `/opt/overlaybd/gzip_cache`, `/opt/overlaybd/cred.json`, `/var/log/overlaybd.log`, and `/var/log/overlaybd-audit.log`.

Dependencies and integration: Installed to `/etc/overlaybd/overlaybd.json` and parsed by `ImageService::read_global_config_and_set`.

Risks and test signals: Gzip cache consumes extra disk when enabled. Tests should start daemon with this default and verify cache directory creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd.json -->
