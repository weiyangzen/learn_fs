# sources/distributed-fs/openafs/src/afs/unified_afs.p.h

Purpose: provides fallback errno definitions so generated/unified AFS code can compile on platforms missing specific errno constants.

Important APIs/types: includes NT errno mapping for `AFS_NT40_ENV`, requires `EIO`, maps missing `EDQUOT` to `ENOSPC`, and maps many other missing errno constants to `EIO`.

Control flow: compile-time preprocessor fallback list only. If `EIO` is absent, compilation fails because there is no safe common fallback.

State and persistence: none.

Dependencies and integration points: used by generated prototype/unified code and cross-platform builds where error constants vary. Volume/cache code relies on named errors such as `ENETDOWN`, `VBUSY`, `EDQUOT`, and `EROFS` being defined.

Risks: mapping unknown errors to `EIO` preserves compilation but collapses semantics, potentially hiding distinctions between retryable, permission, quota, network, and stale-handle failures on deficient platforms. Adding a fallback can affect conditional code that uses `#ifdef` to detect platform capabilities.

Test signals: preprocess on minimal/Windows-like environments, verify required errno names compile, and confirm runtime error translation still distinguishes important cases on full POSIX platforms where native constants exist.
