## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/utils.rs

### Purpose
`nvmx/utils.rs` centralizes small NVMe status and event constants used by the controller and handle layers.

### Important APIs, Types, And Functions
`nvme_cpl_is_pi_error()` detects guard, application tag, and reference tag media errors. `nvme_cpl_succeeded()` checks generic success status. Public enums expose media error codes, AER event types, notice info, NVM command set info, and dataset-management attributes.

### Control Flow
Both completion helpers read status-code type and status-code fields from an SPDK completion. PI detection matches media error SCT plus one of the three protection-information status codes. Success detection matches generic SCT and success SC.

### State, Persistence, And Dependencies
There is no state. The file depends only on SPDK completion layout from `spdk_rs`.

### Integration Points
`handle.rs` uses PI and success helpers for I/O completion logging and passthrough/admin completion mapping. `controller.rs` uses AER enum values to interpret async event completions. `handle.rs` uses `NvmeDsmAttribute::Deallocate` for unmap.

### Risks
The helper assumes the bindgen status bitfield layout matches the SPDK/NVMe headers in use. New NVMe status types or PI codes would require updates. Null completion pointers would be unsafe.

### Test Signals
Unit tests can construct synthetic completions for generic success, generic failure, each PI media error, non-PI media errors, null-safety expectations, and AER value matching used in `controller.rs`.
