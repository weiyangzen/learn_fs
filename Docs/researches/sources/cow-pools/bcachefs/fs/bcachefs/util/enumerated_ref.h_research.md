# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.h

This header defines the public enumerated-ref API and inline production implementation.

Main API:
- `enumerated_ref_get()`
- `__enumerated_ref_tryget()`
- `enumerated_ref_tryget()`
- `enumerated_ref_put()`
- `enumerated_ref_is_zero()`
- `enumerated_ref_stop_async()`
- `enumerated_ref_stop()`
- `enumerated_ref_start()`
- `enumerated_ref_exit()`
- `enumerated_ref_init()`
- `enumerated_ref_to_text()`

Production-mode behavior:
- `get`/`tryget`/`put` call `percpu_ref_*`.
- `enumerated_ref_tryget()` uses `percpu_ref_tryget_live()`.
- `enumerated_ref_is_zero()` uses `percpu_ref_is_zero()`.

Debug-mode behavior:
- Function declarations are used so `enumerated_ref.c` can track refs per caller category.
- `enumerated_ref_is_zero()` scans all indexed debug refs.

Research notes:
- The API accepts an index even in production mode, giving callers stable attribution points with no production overhead beyond ignored parameters.
