<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h

Purpose: Forwarding wrappers that preserve cache-specific methods while delegating to Photon forward filesystems/files.

APIs and types: `ForwardCachedFileBase` forwards `get_source`, `set_source`, `get_store`, and `query`. `ForwardCachedFSBase` forwards `get_source`, `set_source`, `get_pool`, and `set_pool`. Type aliases provide ownership and non-ownership variants.

State and persistence: No state beyond wrapped `m_file` or `m_fs`.

Dependencies and integration: Useful for instrumentation or layering around `ICachedFile`/`ICachedFileSystem` without losing cache APIs.

Risks and test signals: Template protected inheritance assumes Photon forward base layout. Compile-time use catches API drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/forwardcfs.h -->
