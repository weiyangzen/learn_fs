<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs

Purpose: Test helpers for SPDK error vbdev creation and error injection.

Important APIs: re-exports SPDK read/write I/O type constants; defines `VBDEV_IO_FAILURE = 1`; `create_error_bdev(error_device, backing_device)` creates an AIO bdev around the backing file/device and then wraps it with `vbdev_error_create`; `inject_error(error_device, op, mode, count)` builds `vbdev_error_inject_opts` and calls `vbdev_error_inject_error`.

Control flow: all FFI calls are unsafe and immediately asserted to return zero. The injection CString is converted with `into_raw` and not reclaimed.

State and dependencies: mutates global SPDK bdev graph and error injection state. Depends on `spdk-rs` raw libspdk bindings.

Risks and test signals: assert-based error handling is acceptable for tests but poor diagnostics. The raw CString leak in `inject_error` is small but repeated use can accumulate. Validate by creating an error bdev, injecting read/write failures, and observing expected I/O failures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs -->
