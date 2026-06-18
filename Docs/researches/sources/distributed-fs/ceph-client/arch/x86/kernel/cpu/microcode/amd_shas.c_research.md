# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/amd_shas.c

Purpose: provides the static SHA256 digest allowlist used by the AMD microcode loader to authenticate selected Zen-family microcode patch payloads whose signing algorithm requires an additional kernel-side digest check.

Important APIs/types/functions: this file defines only `static const struct patch_digest phashes[]`, consumed by `amd.c`. Each entry maps a `patch_id` to a 32-byte SHA256 digest. It relies on `struct patch_digest` and `SHA256_DIGEST_SIZE` being defined before inclusion, because `amd.c` includes this C fragment directly rather than compiling it as a separate translation unit.

Control flow: there is no executable control flow in this file. `amd.c` calls `bsearch()` over `phashes` from `verify_sha256_digest()`, using `cmp_id()` and the patch ID from the AMD microcode header. If a matching digest exists, `amd.c` hashes the patch data and compares it against the stored digest before writing the patch loader MSR.

State and persistence: state is immutable `.rodata` compiled into the kernel image. There is no allocation, I/O, runtime mutation, or persistence beyond the kernel binary.

Dependencies and integration points: tightly coupled to `amd.c`; the comment requires entries to remain sorted because binary search is used. It indirectly participates in AMD early and late microcode loading, and its coverage must match the cutoff revisions in `get_cutoff_revision()`.

Risks: an unsorted entry silently breaks binary search for some patch IDs. Missing, stale, or mistyped digests cause legitimate patches to be rejected, while an incorrect digest would weaken the mitigation this table is meant to provide. Since this is included C data, duplicate symbol or type changes in `amd.c` can break compilation.

Test signals: build coverage for `CONFIG_CPU_SUP_AMD`, binary-search lookup for first/middle/last patch IDs, rejection of intentionally corrupted patch data, successful load for every listed patch ID, and validation that the generated object contains `phashes` only as private data.
