# sources/distributed-fs/ceph-client/io_uring/bpf_filter.c

## Purpose
`bpf_filter.c` implements classic BPF-based filtering for io_uring request submission. Filters are registered per opcode and can allow or deny requests based on a restricted context populated from the request.

## Important APIs, Types, And Functions
- `struct io_bpf_filter` links a refcounted `bpf_prog` list per opcode.
- `__io_uring_run_bpf_filters()` runs all filters for `req->opcode`; any zero result denies with `-EACCES`.
- `io_register_bpf_filter()` imports user registration data, creates a BPF program, copy-on-writes cloned filter sets if needed, and installs the filter.
- `io_put_bpf_filters()` and `io_free_bpf_filters()` manage RCU/refcounted cleanup.
- `io_bpf_filter_clone()` shares filters into cloned restrictions with COW.
- `io_uring_check_cbpf_filter()` validates and rewrites a safe cBPF instruction subset.

## Control Flow
Registration validates command type, flags, opcode, reserved fields, filter length, and expected per-opcode PDU size. It then creates a BPF program from user instructions, allocates or COWs the filter table, prepends the new filter for the opcode, and optionally marks all unregistered opcodes with `dummy_filter` to deny the rest. Runtime filtering does a fast RCU pointer check, populates `io_uring_bpf_ctx`, then runs each filter pinned on CPU until all allow or one denies.

## State And Persistence
Filter state is stored in `struct io_restriction` through `bpf_filters` and `bpf_filters_cow`. The filter table is an RCU array indexed by opcode; individual filter lists are refcounted and immutable except for prepending. `dummy_filter` is a static sentinel for deny-all slots.

## Dependencies And Integration Points
The file depends on io_uring opcode definitions (`io_issue_defs`), operation-specific filter population callbacks, classic BPF creation/validation, RCU, spinlocks, and restriction registration paths. The header provides disabled stubs when `CONFIG_IO_URING_BPF` is off.

## Risks And Edge Cases
Verifier safety is central: only aligned loads from the bounded io_uring context and selected ALU/jump operations are allowed. COW and refcount handling must avoid use-after-free while cloned restrictions are modified. `DENY_REST` changes default behavior for all unspecified opcodes, which can surprise callers if combined with later filter additions.

## Test Signals
Tests should cover allowed/denied opcodes, stacked filters, invalid cBPF instructions, strict and non-strict PDU size handling, cloned restrictions with COW, `DENY_REST`, and RCU teardown under concurrent submissions.
