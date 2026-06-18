<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_unix.go -->
# sources/cloud-native/moby/daemon/images/image_unix.go

Purpose: provides Unix implementation of container layer size reporting for the image service.

Important APIs and control flow: `GetLayerFolders` panics because it is Windows-specific. `GetContainerLayerSize` gets the container RW layer, logs and returns zeroes if unavailable, gets RW diff size, returns `-1` for RW size on driver errors, adds parent size when present, and releases the RW layer.

State and persistence: reads graphdriver/layer-store size metadata and releases a layer reference; no state is written.

Dependencies and integration: used by container inspect size reporting on Linux/FreeBSD. Depends on layer-store RW layer APIs and containerd logging.

Risks: errors getting the RW layer are intentionally logged but not returned, preserving historical API behavior. The function returns `-1` for RW size on size errors, which callers must interpret correctly.

Test signals: container inspect tests exercise size paths indirectly; this file has no direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_unix.go -->
