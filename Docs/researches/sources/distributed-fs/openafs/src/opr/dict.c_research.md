# sources/distributed-fs/openafs/src/opr/dict.c

Purpose: allocation/free implementation for a simple hash-bucket dictionary backed by `opr_queue` chains.

Important APIs/types/functions: `opr_dict_Init(size)` allocates `struct opr_dict`, validates that size is a power of two, allocates a table of queue heads, and initializes each. `opr_dict_Free` frees the table and dictionary and nulls the caller pointer.

Control flow: no lookup logic lives here; bucket insertion, scanning, and promotion are static inline helpers in `dict.h`.

State and persistence: heap-allocated dictionary table only. No persistence and no element ownership beyond bucket heads.

Dependencies/integration: includes `dict.h`, which depends on `opr/queue.h`. Used by `opr_cache`.

Risks and test signals: callers must free or detach all elements before `opr_dict_Free`. Non-power-of-two sizes fail. Tests should validate init failure for invalid sizes and bucket initialization.
