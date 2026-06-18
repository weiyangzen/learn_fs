<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/layer.rs -->
# sources/cloud-native/fuse-overlayfs/src/layer.rs

Purpose: overlay layer initialization and metadata wrapper.

Important APIs and flow: `OvlLayer` stores a boxed `DataSource` and whether it is a lower layer. `init_layers` parses lowerdir entries, initializes optional upper first, applies `xattr_permissions` override when no xattr mode was detected, enforces `xino=on` NFS file handle support, skips unimplemented plugin lowerdirs with warnings, initializes direct lower layers, and errors if no layers are specified. `all_same_device` checks whether every layer has the same device ID.

State and integration: opens layer root file descriptors through `DirectAccess`; no writes except any side effects of opening/probing. Risks include skipped plugin layers silently changing layer stack, strict xino support failures, and upper being index 0 as an important invariant for copy-up and overlay operations. Test signal comes from config/layer and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/layer.rs -->
