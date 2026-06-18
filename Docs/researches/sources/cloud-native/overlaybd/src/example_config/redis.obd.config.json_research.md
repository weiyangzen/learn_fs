<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json -->
# sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json

Purpose: Example image config for a read-only Redis image backed by remote registry blobs.

APIs and control flow: Sets `repoBlobUrl`, seven lower layer records with `digest`, `size`, and local `dir`, empty upper config for read-only behavior, and a `resultFile`.

State and persistence: Background download may populate `/var/lib/overlaybd/test/<n>/.download` and `overlaybd.commit`; init status is written to `/var/lib/overlaybd/init-debug.log`.

Dependencies and integration: Used by CI configfs command `dev_config=overlaybd/.../redis.obd.config.json`.

Risks and test signals: Remote Docker Hub availability and credentials can affect opens. Mounting read-only and listing files validate the config.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/redis.obd.config.json -->
