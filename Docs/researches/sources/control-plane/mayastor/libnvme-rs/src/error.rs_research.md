# sources/control-plane/mayastor/libnvme-rs/src/error.rs

Purpose: typed error enum for libnvme wrapper operations.

Important APIs/types/functions: `NvmeError` derives `Snafu` and includes `IoError`, `LookupHostError`, `CreateCtrlrError`, `AddCtrlrError`, `FileIoError`, and `UrlError`. `From<std::io::Error>` maps I/O failures into `IoError`.

Control flow: wrapper functions construct variants with libnvme return codes or URL parse errors and return `Result<_, NvmeError>`.

State/persistence: carries return codes and source errors only.

Dependencies/integration: used by `NvmeTarget` connect/disconnect/list parsing paths and exposes failure reasons to callers.

Risks: display strings for some variants omit the source value text after `IO error:`. Return code sign conventions vary by libnvme call and need caller interpretation.

Test signals: URI parse tests indirectly exercise `UrlError`; runtime NVMe tests would exercise libnvme return-code variants.
