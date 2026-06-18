# sources/distributed-fs/ceph/src/mds/RetryRequest.h

Purpose: declares request-retry contexts for `MDRequestRef` operations that need to be rescheduled after locks or cache conditions change.

Important APIs and types: `C_MDS_RetryRequest` stores an `MDCache*` and `MDRequestRef` and implements `finish()` in the corresponding source file elsewhere. `CF_MDS_RetryRequestFactory` stores the same request plus a `drop_locks` flag and builds retry contexts.

State and persistence: the header defines only in-memory retry state. It does not persist request state; it relies on `MDRequestRef` lifetime and MDCache request machinery.

Dependencies and integration: includes `MDCache.h` and `MDSContext.h`. Comments in nearby `CDir.cc` indicate retry requests can drive damage-table paths after blocked operations resume.

Risks and test signals: the main risk is lock ownership: retry factories that drop locks must match the wait condition that caused the retry. Tests should verify that retried metadata requests do not retain invalid locks, do not double-complete, and re-enter MDCache through the expected dispatch path.
