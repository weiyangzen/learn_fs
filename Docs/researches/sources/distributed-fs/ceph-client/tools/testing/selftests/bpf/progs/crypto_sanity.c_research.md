<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c

## Purpose
`crypto_sanity.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3848 bytes across 179 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: dynptr construction/access/mutation helpers; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_create`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_dynptr_adjust`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_skb_load_bytes`, `bpf_skb_pull_data`.
Attach sections and exported entry points:
- line 53 `SEC("syscall")` -> int skb_crypto_setup(void *ctx)
- line 85 `SEC("tc")` -> int decrypt_sanity(struct __sk_buff *skb)
- line 132 `SEC("tc")` -> int encrypt_sanity(struct __sk_buff *skb)
- line 179 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 20 `skb_dynptr_validate`: `static int skb_dynptr_validate(struct __sk_buff *skb, struct bpf_dynptr *psrc)`
- line 54 `skb_crypto_setup`: `int skb_crypto_setup(void *ctx)`
- line 86 `decrypt_sanity`: `int decrypt_sanity(struct __sk_buff *skb)`
- line 133 `encrypt_sanity`: `int encrypt_sanity(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `tc`, `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `skb_dynptr_validate`, `skb_crypto_setup`, `decrypt_sanity`, `encrypt_sanity`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 14 `u16 udp_test_port = 7777;`
- line 15 `u32 authsize, key_len;`
- line 16 `char algo[128] = {};`
- line 17 `char dst[16] = {}, dst_bad[8] = {};`
- line 18 `int status;`
- line 24 `u32 offset;`
- line 62 `int err;`
- line 91 `int err;`
- line 138 `int err;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c -->
