# sources/distributed-fs/eos/mgm/proc/user/DfCmd.cc

## Purpose

`DfCmd.cc` implements the protobuf-backed `DfCmd` command body. It returns EOS filesystem capacity and usage information by delegating directly to `FsView::gFsView.Df()`.

## Important APIs, Types, and Functions

The only method is `eos::console::ReplyProto DfCmd::ProcessRequest() noexcept`. It extracts `eos::console::DfProto df = mReqProto.df()` and passes `df.monitoring()`, `df.si()`, `df.readable()`, `df.path()`, and `WantsJsonOutput()` to `FsView::gFsView.Df()`.

## Control Flow

The method constructs a reply, delegates formatting and data retrieval to `FsView`, stores the returned string as `std_out`, sets `retc` to 0, and returns. No local validation or exception handling is present in this file.

## State and Persistence

`DfCmd.cc` does not mutate state. It reads the current filesystem view through `FsView`; any freshness, locking, and filtering semantics are owned by that subsystem.

## Dependencies and Integration Points

It includes `DfCmd.hh`, `XrdMgmOfs`, `FsView`, and config headers. Its main integration point is the protobuf console request/reply command path, replacing older opaque-command style for `df`.

## Risks and Test Signals

The thin wrapper means risk is mostly contract drift with `DfProto` or `FsView::Df()`. Since `retc` is always 0, errors must be encoded by `FsView::Df()` if needed. Test signals include monitoring output, SI units, human-readable output, path filtering, JSON output, and behavior when the filesystem view is empty or partially unavailable.
