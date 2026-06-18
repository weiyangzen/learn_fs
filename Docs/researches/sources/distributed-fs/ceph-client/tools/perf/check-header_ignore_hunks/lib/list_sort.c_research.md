# sources/distributed-fs/ceph-client/tools/perf/check-header_ignore_hunks/lib/list_sort.c

### Purpose
This file is not C source; it is a diff hunk allowlist used by `check-headers.sh` when comparing `tools/lib/list_sort.c` against the kernel's `lib/list_sort.c`. It records an intentional difference to ignore.

### Important APIs, Types, And Functions
The hunk adds a local `u8 count` and a periodic `cmp(priv, b, b)` callback in the remainder-linking loop of `list_sort` merge logic. The comment explains that highly unbalanced merges, such as already sorted input, may otherwise run many iterations without comparator callbacks, so the callback gives clients a chance to call `cond_resched()`.

### Control Flow
`check-headers.sh` pipes unified diff output through `grep -vf` using this file. Lines matching this hunk are filtered before counting remaining differences.

### State And Persistence
The file persists an expected synchronization exception. It has no runtime state.

### Dependencies And Integration Points
It is tightly coupled to `tools/perf/check-headers.sh` and the textual shape of the upstream diff for `lib/list_sort.c`.

### Risks
Because this is pattern-based diff filtering, upstream edits can make the ignore hunk fail to match or accidentally match too broadly. The file must be reviewed whenever `list_sort.c` is resynced.

### Test Signals
Run `tools/perf/check-headers.sh` from a full kernel tree and verify `lib/list_sort.c` does not report a failure except for new, real differences.
