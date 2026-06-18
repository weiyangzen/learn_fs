# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/update.h

Public types and APIs for data update/move operations.

Key contents:
- Defines `BCH_DATA_UPDATE_TYPES()` for other, copygc, reconcile, promote, self-heal, scrub, and scrub_no_repair.
- `struct data_update_opts` carries pointer kill masks, EC kill masks, extra replicas, target, read device/flags, write flags, commit flags, and checksum paranoia.
- `struct data_update` stores saved old key, options, in-flight hash state, device refs, moving-context links, read bio, write op, and allocated bvecs.
- `struct promote_op` embeds a `data_update` plus work item and inline bvec storage for read promotion.
- Declares text/debug helpers, in-flight lookup, index update, read completion, feasibility checks, EC allocation failure handling, init/exit, pointer-mask remap, and fs init/exit.

Important invariants:
- `cas[]` is parallel to extent pointers and records held device refs.
- `data_update` owns both read and write state because move-path operations read an existing extent then write replacement replicas.
