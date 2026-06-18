# sources/distributed-fs/ceph-client/kernel/bpf/mprog.c

Purpose: implements generic multi-program attach/detach/query operations for BPF attach points that maintain ordered arrays of programs and optional links. It supports positional insertion before/after existing programs, replacement, deletion from exact/front/back positions, and revision-based stale-update detection. The source was read as a complete 452-line file.

Important APIs/functions: `bpf_mprog_attach`, `bpf_mprog_detach`, `bpf_mprog_query`, plus internal `bpf_mprog_link`, `bpf_mprog_prog`, `bpf_mprog_tuple_relative`, `bpf_mprog_replace`, `bpf_mprog_insert`, `bpf_mprog_delete`, `bpf_mprog_pos_exact`, `bpf_mprog_pos_before`, `bpf_mprog_pos_after`, and `bpf_mprog_fetch`. Important types are `struct bpf_mprog_entry`, `struct bpf_mprog_fp`, `struct bpf_mprog_cp`, and `struct bpf_tuple`.

Control flow: relative arguments are converted from an ID or FD into a tuple containing a refcounted link or program. Attach first checks revision, duplicate program insertion, replacement target, max capacity, and before/after constraints; if all selected rules agree on one index, it either writes in place for replacement or copies to the peer entry, grows the peer, inserts the tuple, and increments revision/count. Detach similarly resolves optional relative tuple and exact target, fetches the program/link at the final index, rejects deleting link-owned programs from non-link paths, then copies/shrinks the peer and marks the removed tuple for later release. Query copies revision, count, program IDs, and optional link IDs to user memory.

State and persistence: the attach point stores ordered `bpf_mprog_entry` arrays. Mutations use a peer/double-buffer style so readers can continue using the old entry until the owner publishes `entry_new`. Program/link references acquired for relative lookups are released before return. Removed tuples are marked for release through the mprog infrastructure rather than freed inline.

Dependencies/integration: relies on helpers from `<linux/bpf_mprog.h>`, BPF link/prog ID and FD lookup APIs, user-copy helpers, and attach-point-specific locking/publishing outside this file. It is a shared engine for BPF subsystems that support multiple ordered programs.

Risks and edge cases: before/after/replacement flags can produce conflicting positions and must fail with `-ERANGE`/specific lookup errors. Revision mismatches return `-ESTALE`. Link/program tuple matching returns `-EBUSY` when the same program is present under a different link ownership. Query truncation returns `-ENOSPC` after copying as much as requested. Capacity is capped by `bpf_mprog_max()`.

Test signals: attach-point selftests for ordered multi-attach, before/after by FD and ID, replacement, deletion of first/last/exact entries, link-owned deletion rejection, stale revision, duplicate attach, query truncation, and mixed link/program arrays.
