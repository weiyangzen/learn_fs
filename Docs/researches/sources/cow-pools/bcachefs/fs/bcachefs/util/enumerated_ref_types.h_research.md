# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref_types.h

This header defines `struct enumerated_ref`.

Fields:
- Debug mode:
  - number of categories
  - dying flag
  - per-category `atomic_long_t` refs
- Normal mode:
  - one `struct percpu_ref`
- Shared:
  - optional stop callback
  - shutdown completion

Research notes:
- The structure is intentionally dual-mode: detailed attribution for debug builds, minimal production refcounting otherwise.
