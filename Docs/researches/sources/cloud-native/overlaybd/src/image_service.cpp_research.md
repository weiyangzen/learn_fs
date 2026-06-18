<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.cpp -->
# sources/cloud-native/overlaybd/src/image_service.cpp

Purpose: Owns global configuration, registry access, cache layers, metrics/exporter, API server, credentials, and active image file registry.

APIs and control flow: Helpers parse blob URLs and auth entries, load credentials from file/http/https with optional mTLS, set result files, derive cache names, and probe P2P accelerator connectivity. `init` reads config, configures logging/audit, creates registryfs v1/v2 with CA certs and user agent, wraps metrics, creates file/ocf/download cache, optional gzip cache, and optional snapshot API server. `enable_acceleration` toggles registry acceleration and chooses `remote_fs`. `create_image_file` merges default download config, parses image config, creates `ImageFile`, and writes success/failure to `resultFile`. Register/find/unregister manage dev_id mapping.

State and persistence: Creates cache dirs/media files, OCF namespace/media, log/audit files, gzip cache dir, result files, and in-memory active-image map.

Dependencies and integration: RegistryFS, cache factories, MetricFS, ExporterServer, ApiServer, ConfigUtils, Photon curl/socket/localfs.

Risks and test signals: Destructor deletes `srcfs` after `cached_fs`, but metric wrapping ownership needs care. Credential URL query is not escaped. Tests should cover cache modes, auth modes, exporter/API startup, and duplicate dev ids.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.cpp -->
