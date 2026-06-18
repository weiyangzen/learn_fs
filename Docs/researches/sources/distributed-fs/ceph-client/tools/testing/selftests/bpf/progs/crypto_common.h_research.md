<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h

## Purpose
`crypto_common.h` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1735 bytes across 66 lines.

## Important APIs, Types, and Functions
- Dependencies: `"errno.h"`, `<stdbool.h>`.
- Important macros/constants: `_CRYPTO_COMMON_H`.
- BPF API surface: map lookup/update/delete or map-side state; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_acquire`, `bpf_crypto_ctx_create`, `bpf_crypto_ctx_release`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 24 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 28 `SEC(".maps")` -> static inline struct __crypto_ctx_value *crypto_ctx_value_lookup(void)
Key functions/subprograms:
- line 14 `bpf_crypto_encrypt`: `int bpf_crypto_encrypt(struct bpf_crypto_ctx *ctx, const struct bpf_dynptr *src,`
- line 16 `bpf_crypto_decrypt`: `int bpf_crypto_decrypt(struct bpf_crypto_ctx *ctx, const struct bpf_dynptr *src,`
- line 37 `crypto_ctx_insert`: `static inline int crypto_ctx_insert(struct bpf_crypto_ctx *ctx)`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_crypto_encrypt`, `bpf_crypto_decrypt`, `crypto_ctx_insert`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 32 `u32 key = 0;`
- line 41 `u32 key = 0;`
- line 42 `int err;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h -->
