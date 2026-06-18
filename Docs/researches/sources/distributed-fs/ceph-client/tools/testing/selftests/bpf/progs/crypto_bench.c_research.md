<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c

## Purpose
`crypto_bench.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2011 bytes across 107 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: dynptr construction/access/mutation helpers; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_create`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`.
Attach sections and exported entry points:
- line 21 `SEC("syscall")` -> int crypto_setup(void *args)
- line 55 `SEC("tc")` -> int crypto_encrypt(struct __sk_buff *skb)
- line 83 `SEC("tc")` -> int crypto_decrypt(struct __sk_buff *skb)
- line 107 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 22 `crypto_setup`: `int crypto_setup(void *args)`
- line 56 `crypto_encrypt`: `int crypto_encrypt(struct __sk_buff *skb)`
- line 84 `crypto_decrypt`: `int crypto_decrypt(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `tc`, `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `crypto_setup`, `crypto_encrypt`, `crypto_decrypt`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `const volatile unsigned int len = 16;`
- line 14 `char cipher[128] = {};`
- line 15 `u32 key_len, authsize;`
- line 16 `char dst[256] = {};`
- line 17 `u8 key[256] = {};`
- line 18 `long hits = 0;`
- line 19 `int status;`
- line 30 `int err = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c -->
