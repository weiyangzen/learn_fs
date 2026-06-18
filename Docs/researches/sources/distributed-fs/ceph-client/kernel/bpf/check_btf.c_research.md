# sources/distributed-fs/ceph-client/kernel/bpf/check_btf.c

## Purpose
`check_btf.c` validates BTF metadata supplied with a BPF program load. It handles function info, line info, and CO-RE relocations, links BTF function names into verifier subprogram metadata, and enforces that abnormal-return instructions in subprograms have compatible BTF return types.

## Important APIs, types, and functions
The public entry points are `bpf_check_btf_info_early()` and `bpf_check_btf_info()`. Validation helpers include `check_abnormal_return()`, `check_btf_func_early()`, `check_btf_func()`, `check_btf_line()`, and `check_core_relo()`. State is stored in `prog->aux->btf`, `func_info`, `func_info_cnt`, `func_info_aux`, `linfo`, `nr_linfo`, and each `subprog_info[*].name` and `linfo_idx`.

## Control flow
The early pass obtains the user BTF by fd when func or line info is present, rejects kernel BTF as program metadata, copies function records with tail-zero checks, validates record sizes, strictly increasing instruction offsets, and BTF func/prototype type IDs, and stores the records. If no func info is present, it rejects `LD_ABS` or `tail_call` in non-main subprograms because return type information is unavailable. The later pass requires the number of func records to match subprogram count, checks each func record offset against the verifier subprogram layout, records linkage and names, validates abnormal-return subprograms return a scalar int-like type, validates line records and subprogram coverage, and applies CO-RE relocation records one at a time to target instructions.

## State and persistence
BTF, function info, auxiliary function info, and line info persist in `bpf_prog_aux` for the lifetime of the loaded program and are later used by verifier diagnostics, kallsyms names, stack/source reporting, and JIT line mappings. CO-RE relocations mutate the program instruction stream during load; relocation records themselves are not retained here. Failed checks free newly allocated arrays on the failing path, while the retained BTF reference is owned by the program aux after early success.

## Dependencies and integration points
The file depends on BPF syscall load attributes, `bpfptr_t` copy helpers for user or kernel attributes, BTF type lookup and string lookup, verifier-discovered subprogram layout, `bpf_core_apply()`, and program aux metadata consumed by `core.c` and verifier logging. It is tightly ordered with subprogram discovery: early function record validation can run before final subprogram matching, and the full pass relies on `env->subprog_info`.

## Risks and test signals
Risks include record-size compatibility bugs, nonzero tail handling, leaked BTF references after partial failure, mismatches between BTF func offsets and subprogram discovery, missing line records for subprogram starts, allowing abnormal returns from non-int functions, and CO-RE relocation offset unit confusion because relocations use byte offsets divided by 8. Test signals include old and new record sizes, invalid type IDs, non-monotonic offsets, no-BTF subprograms with `LD_ABS` or `tail_call`, func count mismatch, line info covering every subprogram, malformed BTF strings, CO-RE relocation bounds, and user-kernel attribute pointer modes.
