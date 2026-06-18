# sources/control-plane/mayastor/io-engine/src/core/fault_injection/inject_io_ctx.rs

## Purpose
Carries I/O metadata from hot I/O paths into the fault-injection matcher. It abstracts over block-device references and plain device names while exposing operation, block range, and mutable I/O vectors.

## Important APIs, Types, and Functions
- `InjectIoDevice` can be `None`, `BlockDevice(*mut dyn BlockDevice)`, or `DeviceName(*const str)`.
- `InjectIoCtx::new(domain)` creates an invalid placeholder context.
- `InjectIoCtx::with_iovs(domain, dev, io_type, offset, num_blocks, iovs)` builds a full context.
- Match helpers include `is_valid`, `domain_ok`, `device_name_ok`, `io_type_ok`, and `block_range_ok`.
- `iovs_mut()` returns mutable I/O vectors for data corruption injection.

## Control Flow and State
I/O paths create a context at submission or completion time and pass it to `inject_submission_error` or `inject_completion_error`. The injection logic filters contexts by domain, target device, read/write operation, and overlapping block range. Data injection requests mutable I/O vectors only after all matching logic succeeds.

State is borrowed raw pointer state. Nothing is owned or persisted by the context.

## Dependencies and Integration Points
Uses `spdk_rs::IoType`, `spdk_rs::IoVec`, and `core::BlockDevice`. Created from nexus child and block-device paths, plus bdev I/O fn-table injection.

## Risks and Test Signals
The enum stores raw trait-object and string pointers. The caller must guarantee the referenced device/string and I/O vectors outlive injection evaluation. `iovs_mut` permits mutation through `&self`, guarded only by pointer checks. Tests should exercise range overlap edges, read/write matching, device-name matching through both variants, and null/empty/uninitialized iov handling.
