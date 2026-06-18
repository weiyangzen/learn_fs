# sources/distributed-fs/eos/mgm/drain/DrainTransferJob.hh

## Purpose
Declares the per-file drain transfer job and progress handler. The class is generic enough to support drain, balance, repair-excluded RAIN reconstruction, and fsck-like replica adjustment through constructor options.

## Important APIs and Types
- `DrainProgressHandler : XrdCl::CopyProgressHandler` tracks cancellation, progress percentage, bytes transferred, and start timestamp.
- `DrainTransferJob::Status { OK, Running, Failed, Ready }`.
- Constructor parameters configure fid, source/target fsids, excluded sources/destinations, source dropping, app tag, balance mode, triggering VID, and repair-excluded behavior.
- Public methods include `DoIt`, `Cancel`, `ReportError`, `SetStatus`, `GetStatus`, `GetInfo`, `UpdateMgmStats`, `GetFileIdentifier`, and `SetMinTransferRate`.
- Under `IN_TEST_HARNESS`, internals such as `GetFileInfo`, URL builders, `SelectDstFs`, and `DrainZeroSizeFile` become public.

## Control Flow and State
The header defines state for app tag, atomic fid/fsids/status/min rate, tried source set, excluded destination vector, RAIN flags, drop-source/balance flags, progress handler, and VID. Cancellation is cooperative through XrdCl progress callbacks.

## Dependencies and Integration Points
Depends on EOS file ids, filesystem ids, namespace file metadata, protobuf file metadata, XrdCl copy process, logging, and virtual identity. `DrainFs` constructs standard drain jobs, while other subsystems can pass non-default flags.

## Risks
- `mExcludeDsts.insert(mExcludeDsts.begin(), exclude_dsts.begin(), exclude_dsts.end())` is valid but unusual and preserves set iteration order rather than caller order.
- Status is atomic, but fields like tried sources and RAIN flags are not protected; they are intended to be job-thread local.
- Progress percentage divides by total bytes in implementation without zero guard.
- Header comment says `GetInfo` returns a map, but it returns `std::list<std::string>`.

## Test Signals
Tests should use `IN_TEST_HARNESS` to validate URL construction, destination selection, zero-size handling, progress cancellation, status transitions, and info tag formatting.
