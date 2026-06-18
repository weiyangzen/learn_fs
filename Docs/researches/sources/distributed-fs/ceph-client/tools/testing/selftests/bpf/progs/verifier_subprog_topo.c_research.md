# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_topo.c

## Purpose
`verifier_subprog_topo.c` verifies topological ordering of BPF subprogram verification. It covers linear call chains, diamond-shaped call graphs, mixed static/global functions, shared leaves, duplicate calls, `bpf_loop` callbacks, callback-to-subprogram chains, and a no-call program.

## Important APIs, Types, and Functions
The file defines many small static/global subprograms implemented with inline assembly. Main entrypoints are `SEC("?raw_tp")` programs annotated with `__success`, `__log_level(2)`, and `__msg("topo_order[...] = ...")`. It uses `bpf_loop` for callback graph cases and libbpf/BPF helper annotations from `bpf_misc.h`.

## Control Flow
Each test creates a specific call graph and returns. Linear tests call A then B; diamond tests converge on shared leaves; mixed tests combine static and global functions; duplicate tests call the same leaf more than once; callback tests pass a callback to `bpf_loop`, including a callback that calls another leaf. The verifier is expected to log subprogram verification order from leaves toward roots.

## State and Persistence
There is no persistent map or external state. The only state under test is the verifier's call graph, topological sort, and callback subgraph accounting.

## Dependencies and Integration Points
The source depends on verifier logging of `topo_order`, subprogram graph construction, static/global linkage handling, and helper callback recognition for `bpf_loop`. It integrates with optional raw tracepoint test sections and log-level matching.

## Risks and Test Signals
Risks include verifying callers before callees, mishandling shared leaves or duplicate call edges, omitting callback subgraphs, or incorrectly ordering global and static functions. Test signals are precise `topo_order` log lines such as `linear_b`, `diamond_c`, `shared_leaf`, `loop_cb`, and `loop_cb2_leaf` preceding their callers.
