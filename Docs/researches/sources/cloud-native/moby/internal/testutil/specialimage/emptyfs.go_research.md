<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go

Purpose: produces an image whose root filesystem is effectively empty, using a zero-byte or empty layer/config shape for load/import tests. Important APIs are `EmptyFS` and the local `zeroReader`. Control flow writes minimal blobs and metadata into an OCI layout. State is generated blobs and JSON metadata under the target directory. Dependencies include OCI specs and shared blob-writing helpers. Risks include archive/import code treating empty layers specially or rejecting zero-sized content. Test signal is for image-load handling of empty root filesystems.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go -->
