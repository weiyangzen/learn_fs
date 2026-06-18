<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/config.h -->
# sources/cloud-native/overlaybd/src/config.h

Purpose: Declarative JSON configuration schema for image files, global service behavior, credentials, caching, logging, metrics, prefetch, TLS, and API service.

APIs and types: Uses `ConfigUtils::Config` and `APPCFG_PARA` macros. Key structs are `LayerConfig`, `UpperConfig`, `DownloadConfig`, `ImageConfig`, `P2PConfig`, `GzipCacheConfig`, `ExporterConfig`, `CredentialConfig`, `CacheConfig`, `LogConfig`, `PrefetchConfig`, `CertConfig`, `ServiceConfig`, `GlobalConfig`, `AuthConfig`, and `ImageAuthResponse`.

State and persistence: Configs are parsed from `/etc/overlaybd/overlaybd.json`, image config files, and credential JSON; snapshot code renames a new image config over the active config.

Dependencies and integration: Read by `ImageService`, `ImageFile`, credential loading, exporter setup, and API setup.

Risks and test signals: Defaults preserve backward compatibility between legacy top-level cache/log fields and nested configs. Tests should parse old and new example configs.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/config.h -->
