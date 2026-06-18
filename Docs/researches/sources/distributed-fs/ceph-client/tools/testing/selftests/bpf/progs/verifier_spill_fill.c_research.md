# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_spill_fill.c

## Purpose
`verifier_spill_fill.c` is a large verifier fixture for stack spill/fill behavior. It validates pointer spills, scalar spills of different widths, partial overwrites, stack byte initialization, precision tracking through stack slots, unprivileged stack restrictions, and ID/range preservation after fills.

## Important APIs, Types, and Functions
The file declares a ring buffer map and small `.data` buffers used as map-value targets for pointer-offset tests. It uses helpers `bpf_ringbuf_reserve`, `bpf_ringbuf_submit`, `bpf_get_prandom_u32`, and `bpf_ktime_get_ns`. Program sections include `socket`, `tc`, `xdp`, and `raw_tp`. Important annotations include `BPF_F_ANY_ALIGNMENT`, `BPF_F_TEST_STATE_FREQ`, `__log_level(2)`, privileged/unprivileged split expectations, and precise `mark_precise` log fragments.

## Control Flow
Early tests spill and reload valid pointers, skb fields, and ring-buffer memory, then corrupt spilled pointer bytes to distinguish privileged pointer leakage from unprivileged rejection. TC/XDP tests spill bounded and unbounded scalars at different widths and reuse them as packet or ctx offsets. Raw tracepoint tests inspect stack slot byte masks and precision backtracking for 8-, 32-, and 64-bit accesses. Later socket tests exercise narrow writes over 64-bit slots, conditional stack initialization, and stack behavior under the no-perfmon unprivileged model.

## State and Persistence
Persistent state is limited to declared maps and `.data` buffers. The important state is stack-slot metadata: initialized bytes, spilled pointer class, scalar ID, range bounds, precision, and whether partial writes should invalidate or preserve the original spill. Ringbuf reservation also introduces nullable pointer state that must be checked and submitted correctly.

## Dependencies and Integration Points
The file integrates with verifier stack modeling, packet pointer arithmetic, XDP context pointer rules, ringbuf pointer rules, map-value bounds, and unprivileged verifier policy. The selftest runner validates both load outcomes and detailed verifier logs.

## Risks and Test Signals
Risks include pointer leaks through corrupted spills, unsafe acceptance of partially initialized stack reads, stale scalar IDs after width-changing fills, and invalid packet/context pointer arithmetic. Test signals include expected verifier errors such as `attempt to corrupt spilled`, `invalid read from stack`, `math between pkt pointer and register with unbounded min value`, `dereference of modified ctx ptr`, and `math between ctx pointer and 4294967295`, plus success logs proving precise stack masks and processed-instruction counts.
