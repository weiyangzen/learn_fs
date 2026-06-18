# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-abi.h

Purpose: `rseq-abi.h` defines the userspace/kernel ABI structures and constants for restartable sequences as consumed by the selftests. It mirrors the syscall-facing contract: registration states, unregister flags, critical-section flags, the critical-section descriptor, and the per-thread `struct rseq_abi` layout.

Important APIs, types, and functions: key types are `enum rseq_abi_cpu_id_state`, `enum rseq_abi_flags`, `enum rseq_abi_cs_flags_bit`, `enum rseq_abi_cs_flags`, `struct rseq_abi_cs`, `struct rseq_abi_slice_ctrl`, and `struct rseq_abi`. `struct rseq_abi_cs` records `version`, `flags`, `start_ip`, `post_commit_offset`, and `abort_ip`. `struct rseq_abi` exposes `cpu_id_start`, `cpu_id`, `rseq_cs`, `flags`, `node_id`, `mm_cid`, `slice_ctrl`, and an extensible end marker.

Control flow: this header has no runtime control flow. It supplies declarations used by `rseq.c`, `rseq.h`, and the architecture headers. Runtime code writes `rseq_cs.arch.ptr` before critical sections, the kernel validates the active descriptor, and aborts clear or redirect through the descriptor state.

State and persistence: the ABI state is per-thread TLS once registered. Kernel-updated fields include CPU IDs, node ID, mm CID, and time-slice grant state. User space writes the active critical-section pointer and slice extension request. The alignment attributes are important persistent ABI properties because the kernel expects cache-line-friendly, atomic access to fields.

Dependencies and integration points: it depends on `<linux/types.h>` and byte-order macros. `rseq.c` allocates a TLS instance of this structure, and `rseq.h` uses offsets and feature-size checks to guard access to extension fields such as `node_id`, `mm_cid`, and `slice_ctrl`. `slice_test.c` uses `slice_ctrl` directly.

Risks and test signals: ABI drift is the primary risk. Incorrect alignment, offset, endian handling, or feature-size assumptions can break the syscall contract across all architectures. Test coverage comes indirectly from registration, syscall error checks, per-cpu operation tests, mm-cid tests, and slice extension tests.
