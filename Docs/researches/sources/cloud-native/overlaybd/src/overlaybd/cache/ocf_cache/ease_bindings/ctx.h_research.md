<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h

Purpose: Shared OCF context data types for ease bindings.

APIs and types: Defines rounding macros, `OcfSrcFileCtx` owning a source Photon file plus namespace info/provider/path, `ease_ocf_io_data` carrying iovs, size, seek, block address, source ctx, error, semaphore, and prefetch flag, `ease_ocf_config`, `ease_ocf_queue`, and `get_context_config`.

State and persistence: Source file context deletes its source file on destruction; IO data semaphores synchronize async OCF completions.

Dependencies and integration: Included by provider, volume, and environment bindings.

Risks and test signals: Ownership is raw-pointer based. Tests should verify source file deletion and callback signaling on error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.h -->
