<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.h -->
# sources/cloud-native/overlaybd/src/image_service.h

Purpose: Public service interface and shared global filesystem state for OverlayBD image creation.

APIs and types: `GlobalFs` stores underlay registry fs, remote/source/cache fs, gzip cache fs, OCF media/namespace filesystems, and IO allocator. `ImageService` exposes `init`, `create_image_file`, `enable_acceleration`, image registration lookup methods, global config, metrics, exporter, and API server. Free functions create the service and load credentials.

State and persistence: `m_config_path` selects the global JSON; `m_image_files` maps dev_id to live images.

Dependencies and integration: Included by `main.cpp`, API server, image file, and metrics code.

Risks and test signals: `ImageAuthResponse` is also declared in `config.h`, a duplication that can drift. Compile and credential parsing tests catch schema mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_service.h -->
