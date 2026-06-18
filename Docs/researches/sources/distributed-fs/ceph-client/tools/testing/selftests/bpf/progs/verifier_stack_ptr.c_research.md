# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_stack_ptr.c

## Purpose
`verifier_stack_ptr.c` tests verifier handling of `PTR_TO_STACK` arithmetic, stack bounds, alignment, mixed register/constant offsets, map stores of stack-derived data, and maximum stack size accounting with `may_goto` and JIT behavior.

## Important APIs, Types, and Functions
The file defines `map_array_48b`, an array map with 48-byte values. Programs are mostly `SEC("socket")` naked assembly with one `tc` map lookup/store case. It uses `bpf_map_lookup_elem`, `BPF_MAXINSNS`-style instruction sequences through inline assembly, `INT_MAX`/`limits.h`, and expected verifier messages for stack pointer arithmetic and stack size limits.

## Control Flow
The tests construct stack pointers from `r10`, add immediate or register offsets, perform loads/stores, and exit with known return values when valid. Invalid paths use misaligned accesses, offsets above frame pointer, offsets below the 512-byte stack limit, arithmetic that would overflow, and dynamic pointer math the verifier cannot prove safe. The TC case stores bytes derived from a stack pointer into a map value to verify safe handling. The final cases distinguish stack size >512 rejection from a 512-byte stack with `may_goto` under JIT and non-JIT expectations.

## State and Persistence
Persistent state is limited to `map_array_48b` for the map interaction test. The core state is verifier stack-pointer metadata: fixed offset, variable offset bounds, alignment, stack depth, and whether arithmetic remains within `[fp-512, fp)`.

## Dependencies and Integration Points
The file integrates with socket and TC verifier rules, stack-depth accounting, map-value access, JIT-specific `may_goto` stack accounting, and unprivileged stack pointer range checks. It depends on exact verifier diagnostics such as `misaligned stack access`, `stack pointer arithmetic goes out of range`, `fp pointer offset`, and `stack size 520(extra 8) is too large`.

## Risks and Test Signals
Risks include accepting out-of-frame stack writes, rejecting legal bounded pointer arithmetic, miscomputing dynamic offsets, or accounting `may_goto` stack usage differently between interpreter and JIT. Test signals are valid return values like `0xfaceb00c` and 42 for accepted paths, plus targeted failure messages for alignment, bounds, pointer math, and stack-size violations.
