<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.h -->
# sources/cloud-native/overlaybd/src/image_file.h

Purpose: Defines the `ImageFile` abstraction exposed to TCMU as a Photon `ForwardFile`.

APIs and types: Constants `COMMIT_FILE_NAME` and `SEALED_FILE_NAME` name local layer states. `ImageFile` overrides `fstat`, `preadv`, `pwritev`, `fdatasync`, and `fallocate`, exposes `get_base`, `compact`, `create_snapshot`, `open_lower_layer`, and `set_auth_failed`, and privately manages lower/upper opening plus background download.

State and persistence: Stores copied image config, config path, download list/thread, lower/upper backing files, dev id, block size, size, LBA count, read-only flag, status, and exception message.

Dependencies and integration: Constructed by `ImageService::create_image_file`; used by `main.cpp` SCSI command handlers.

Risks and test signals: Constructor registers the object before init completes and unregisters in destructor. Lifetime tests should verify duplicate dev id rejection and download thread join.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.h -->
