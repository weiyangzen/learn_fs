<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c

## Purpose
`crypto_basic.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1141 bytes across 68 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_acquire`, `bpf_crypto_ctx_create`, `bpf_crypto_ctx_release`.
Attach sections and exported entry points:
- line 12 `SEC("syscall")` -> int crypto_release(void *ctx)
- line 38 `SEC("syscall")` -> int crypto_acquire(void *ctx)
- line 68 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `crypto_release`: `int crypto_release(void *ctx)`
- line 39 `__msg`: `__failure __msg("Unreleased reference")`
- line 40 `crypto_acquire`: `int crypto_acquire(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `syscall`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `crypto_release`, `__msg`, `crypto_acquire`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `int status;`
- line 22 `int err = 0;`
- line 48 `int err = 0;`
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c -->
