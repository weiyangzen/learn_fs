# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-mem-types.h

Purpose: this header reserves GlusterFS memory accounting type IDs for bit-rot-stub and bit-rot daemon allocations.

Important definitions: `enum br_mem_types` starts at `gf_common_mt_end + 1` and includes private state, version buffers, inode contexts, signatures, daemon children/objects/workers, scrubber entries, fd contexts, signature stubs, child events, and miscellaneous allocations. `gf_br_stub_mt_end` is passed to `xlator_mem_acct_init` by both daemon and stub memory accounting entry points.

Control flow and state: no runtime logic is present. The enum values are used by `GF_CALLOC`, `GF_MALLOC`, mem pools, and xlator memory accounting so allocations can be attributed in diagnostics.

Dependencies and integration points: depends on `<glusterfs/mem-types.h>`. It is included by both `bit-rot.c` and `bit-rot-stub.c`, so enum additions affect both components' accounting boundary.

Risks: removing or reordering memory IDs can confuse diagnostics and any tooling that expects stable type names. A shared enum for daemon and stub means new allocations in either component should be added before the end sentinel without collisions.

Test signals: build and run memory accounting initialization for both `bit-rot` and `bitrot-stub`, then exercise signer, scrubber, signature, fd context, and quarantine paths while checking allocation labels.
