<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.h -->
# sources/distributed-fs/coda/coda-src/resolution/compops.h

Purpose: public interface for compensating operation computation during directory resolution.

Important APIs: `ComputeCompOps(olist *, ViceFid *)` returns an `arrlist *` of compensating `rsle` entries for a vnode based on all parsed logs. `PrintCompOps(arrlist *)` emits those entries for diagnostics.

Dependencies/integration: includes `olist`, `arrlist`, and `vcrcommon` for Coda list containers and `ViceFid`. Implemented by `compops.cc` and used by log-based resolution phases to determine which remote operations need replay or conflict handling.

State/persistence: no state of its own. The returned list is an in-memory selection/order over log entries owned elsewhere.

Risks/test signals: ownership of the returned `arrlist` is implied but not documented; callers must delete the list without deleting the underlying `rsle` records unless they own the parsed log buffer. Test callers for leaks and double frees when resolution aborts early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.h -->
