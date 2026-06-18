<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp

Purpose: Supplies OCF context operations for data buffers, cleaner stubs, and logging.

APIs and control flow: Implements iovec/buffer copy helpers, `ctx_data_alloc/free`, read/write/zero/seek/copy operations, no-op mlock/munlock/secure erase, no-op cleaner callbacks, and logger printing through Photon logging. `get_context_config` returns a static `ocf_ctx_config` with these ops.

State and persistence: Allocates OCF IO data through global `g_io_alloc`; each context data owns iov arrays and buffers.

Dependencies and integration: Used by `ease_ocf_provider::start` when creating OCF context.

Risks and test signals: `ctx_logger_print` uses `vsprintf` into a 512-byte buffer, risking overflow. Tests should stress large OCF log lines and data copy offsets.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/ctx.cpp -->
