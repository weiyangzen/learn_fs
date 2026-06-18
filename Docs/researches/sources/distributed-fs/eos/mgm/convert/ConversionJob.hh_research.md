# sources/distributed-fs/eos/mgm/convert/ConversionJob.hh

## Purpose
Declares the conversion job execution object and its XrdCl progress/cancellation handler. It is the public surface used by `ConverterEngine` to run and monitor individual conversion tasks.

## Important APIs and Types
- `enum class ConversionJobStatus { DONE, RUNNING, PENDING, FAILED }`.
- `ConversionProgressHandler` implements `XrdCl::CopyProgressHandler` with atomic cancel/progress/bytes/start-time fields.
- `ConversionJob` exposes constructor, destructor, `DoIt`, `Cancel`, status/error/conversion/fid getters.
- Private helpers `Merge`, `HandleError`, and `ConversionCGI` encapsulate terminal handling, metadata merge, and destination parameter construction.

## Control Flow and State
The header shows lifecycle state: jobs start `PENDING`, can be cancelled through the progress handler, and transition to `RUNNING`, `DONE`, or `FAILED` in the implementation. `mFid` is expected to match `mConversionInfo.mFid`, enforced by an assert in `GetFid`.

## Dependencies and Integration Points
Includes global MGM OFS, conversion info, common file/layout/filesystem types, namespace file metadata, XrdCl copy, and `XrdOucCallBack`. The global `EOS_APP_NAME` defaults conversion app tagging.

## Risks
- `static std::string EOS_APP_NAME` in a header gives each translation unit its own mutable copy; this is not ideal for shared constants.
- `ConversionProgressHandler::JobProgress` divides by `bytesTotal` without guarding zero.
- The callback type is generic and the public contract does not clarify why terminal notification uses `Cancel`.

## Test Signals
Tests should cover progress handler cancellation/progress calculations, status transitions, fid mismatch assertions in debug builds, and compile-time compatibility with engine scheduling code.
