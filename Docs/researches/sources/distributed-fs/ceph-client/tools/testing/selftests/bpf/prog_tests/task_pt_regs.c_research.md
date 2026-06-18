# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_pt_regs.c

Purpose: verifies task pt_regs retrieval for a uprobe context. It attaches `test_task_pt_regs` program to a local noinline trigger function in `/proc/self/exe`.

Control flow gets uprobe offset for `trigger_func`, opens/loads skeleton, attaches `handle_uprobe`, invokes `trigger_func`, checks BSS `uprobe_res == 1`, then compares BSS `current_regs` and `ctx_regs` byte-for-byte. State is uprobe link and BSS register snapshots. Dependencies are uprobe offset helper, self-executable attachment, generated skeleton, and architecture-compatible pt_regs layout. Risks include compiler/linker changing function visibility despite `noinline`, uprobe attach restrictions, and register struct layout sensitivity. Test signals are attach success, trigger result one, and memcmp equality of current and context registers.
