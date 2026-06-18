# sources/distributed-fs/openafs/src/opr/dict.h

Purpose: dictionary structure and inline helpers for queue-backed hash buckets.

Important APIs/types/functions: `struct opr_dict` stores `size` and `table`. Inline helpers `opr_dict_Prepend`, `opr_dict_Append`, and `opr_dict_Promote` map an integer hash to `index & (size - 1)`. Macros `opr_dict_ScanBucket` and `opr_dict_ScanBucketSafe` expose bucket iteration. Declares init/free functions.

Control flow: no standalone runtime flow; helpers perform intrusive queue operations.

State and persistence: no header-owned state. The dictionary does not own user entries.

Dependencies/integration: requires `opr/queue.h` and power-of-two `size` from `opr_dict_Init`. Used by cache and any other small hashed collections.

Risks and test signals: direct masking requires power-of-two sizes. No locking is provided. Caller must avoid using freed or unlinked queue nodes. Cache tests indirectly validate it.
