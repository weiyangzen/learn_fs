# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.h

Public enumerated-ref API. Provides `get`, `tryget`, live `tryget`, and `put` as either debug function calls or inline `percpu_ref` wrappers. Also exposes zero test, stop/start, init/exit, and diagnostic text rendering.

Callers pass an index naming the ref user; in non-debug builds the index is ignored but retained for instrumentation-compatible call sites.
