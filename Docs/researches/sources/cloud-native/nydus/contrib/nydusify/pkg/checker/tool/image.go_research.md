# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image.go

Purpose: provides helper logic for identifying parsed image type and mounting/unmounting OCI image root filesystems from extracted layer directories.

Important APIs and flow: `mkMounts` returns nil for no layers, a read-only recursive bind mount for one layer, and an overlay mount with `lowerdir=<layers joined by colon>` for multiple layers. `CheckImageType` returns `nydus`, `oci`, or `unknown` by inspecting `parser.Parsed`. `Image.Mount` creates the rootfs directory, builds layer directory names in reverse manifest order (`layer-N` down to `layer-0`), escapes colons for overlay lowerdir syntax, and calls `mount.All`. `Image.Umount` tolerates missing rootfs, otherwise calls containerd `mount.Unmount` and removes the rootfs tree.

State and persistence: creates and deletes rootfs directories; performs kernel mount operations. Layer data is assumed to already exist under `LayerBaseDir`.

Dependencies and integration: uses containerd mount package, OCI descriptors, and parser types. It is part of checker comparisons where OCI rootfs must be mounted while Nydus rootfs is mounted by `nydusd`.

Risks and test signals: requires mount privileges at runtime. Overlay lowerdir escaping only handles colon replacement; other unusual paths rely on kernel behavior. Unmount failure prevents cleanup.
