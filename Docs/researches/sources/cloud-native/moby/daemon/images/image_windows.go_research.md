<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_windows.go -->
# sources/cloud-native/moby/daemon/images/image_windows.go

Purpose: provides Windows-specific layer-folder inspection support for image-mounted containers, with a placeholder size implementation.

Important APIs and control flow: `GetContainerLayerSize` currently returns zeros with a TODO. `GetLayerFolders` iterates image rootfs diff IDs, mutates `img.RootFS.DiffIDs` to each prefix, validates OS support, resolves each layer path from the layer store, reverses parent order, then appends the RW layer metadata `dir`.

State and persistence: reads layer paths and RW layer metadata. It mutates the passed image object's `RootFS.DiffIDs` slice while computing paths.

Dependencies and integration: used by Windows container inspect/mount reporting and depends on internal image OS validation plus `layer.GetLayerPath`.

Risks: the in-place `RootFS.DiffIDs` mutation is explicitly marked with a FIXME and can surprise callers if they reuse the image object. Size reporting is not implemented on Windows.

Test signals: no direct tests in this subset; Windows-specific daemon tests would be needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_windows.go -->
