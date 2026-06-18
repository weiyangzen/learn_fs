# sources/cloud-native/overlaybd/src/tools/comm_func.cpp

Purpose: implements shared helpers used by OverlayBD CLI tools for opening files, creating image-service filesystems, wrapping ext4/EROFS, registry uploading, and parsing config/dev-id arguments.

Important APIs/types/functions: `open_file`, `create_overlaybd`, `create_ext4fs`, `is_erofs_fs`, `create_erofs_fs`, `create_uploader`, and `parse_config_and_dev_id`. The functions work with Photon `IFile`, `IFileSystem`, `ImageService`, zfile compression args, registryfs credentials, extfs, subfs, and EROFS helpers.

Control flow: helpers mostly fail fast: a failed open, image-service create, image-file create, mkfs, extfs/subfs creation, credential load, or uploader setup prints diagnostics and exits. `create_ext4fs` optionally formats the image file, creates an ext filesystem, then returns a subfs rooted at the requested path. `create_uploader` loads credentials for an upload URL and wraps a source file in a registry uploader.

State and persistence: mutates underlying image files when `mkfs` is requested and writes upload state through registryfs. No long-lived global state is kept.

Dependencies/integration: included by `overlaybd-apply`, `overlaybd-merge`, `turboOCI-apply`, and other tools; integrates image-service JSON configs with filesystem adaptors and registry uploads.

Risks: helpers call `exit(-1)`, so callers cannot recover. Ownership is caller-managed for returned `IFile` and `IFileSystem` objects. Upload credential lookup depends on URL matching in the credential file.

Test signals: exercised indirectly by all CLI integration tests that open image configs, create extfs/EROFS views, or push merged/committed layers.
