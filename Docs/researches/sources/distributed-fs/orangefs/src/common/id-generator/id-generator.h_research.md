# sources/distributed-fs/orangefs/src/common/id-generator/id-generator.h

Purpose: Declares fast and safe pointer-to-ID mechanisms for OrangeFS.

Important APIs/types: `BMI_id_gen_t` is `PVFS_id_gen_t` when PVFS types are already included, otherwise `int64_t`. `id_gen_fast_register()` casts a pointer directly into an integer ID, `id_gen_fast_lookup()` casts back, and `id_gen_fast_unregister()` is a no-op. Safe registry functions are declared for indirect ID mapping.

Control flow contract: Fast IDs require no initialization but expose pointer values. Safe IDs require initialize/register/lookup/unregister/finalize lifecycle.

State/persistence: Fast IDs encode process-local pointer addresses and are not stable across processes/runs. Safe IDs are process-global registry keys.

Dependencies/integration: Includes `pvfs2-config.h` for `SIZEOF_VOID_P`, and `<stdint.h>/<errno.h>`.

Risks: Fast registration truncates/casts pointers on 32-bit through `int32_t`, then back through `uint32_t`; it is process-local and unsafe for untrusted handles. The typedef changes based on include order if `__PVFS2_TYPES_H` is defined.

Test signals: Validate fast round-trip on 32-bit and 64-bit builds, and safe lifecycle under concurrency.
