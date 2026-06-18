# sources/control-plane/mayastor/io-engine/src/core/fault_injection/bdev_io_injection.rs

## Purpose
Implements low-level SPDK bdev function-table patching for `FaultDomain::BdevIo` injections. This lets tests force NVMe completion statuses before the original bdev `submit_request` handler runs.

## Important APIs, Types, and Functions
- `BdevInfo` records the replacement fn table, original fn table, and associated `Injection`.
- `get_bdevs()` returns the global hash map of patched bdevs.
- `inject_submit_request(chan, io_ptr)` is the replacement SPDK submit callback.
- `add_bdev_io_injection(inj)` validates and installs the patched fn table.

## Control Flow and State
Adding an injection validates submission stage and NVMe-status method, looks up the target `UntypedBdev`, rejects duplicate injection for that bdev, clones the original `spdk_bdev_fn_table`, replaces `submit_request` with `inject_submit_request`, writes the new function table pointer into the bdev, and stores metadata keyed by replacement table pointer. On submit, the callback reconstructs `BdevIo`, builds an `InjectIoCtx`, asks the injection whether it applies, completes the I/O with an NVMe status if so, or forwards to the original `submit_request`.

State is global and process-local. The code does not restore original fn tables on removal in this file.

## Dependencies and Integration Points
Feature gated under `fault-injection`. Called by `injection_api::Injections::add` when the domain is `BdevIo`. Depends on SPDK raw structs and `spdk_bdev_io_complete_nvme_status`.

## Risks and Test Signals
This is highly unsafe: it mutates SPDK bdev internals and leaks replacement function tables. Removal from the main injection list does not undo the bdev hook. Multiple injections per bdev are rejected. Tests should verify validation errors, forwarding to original callback, exact NVMe completion status, duplicate rejection, and behavior after injection removal.
