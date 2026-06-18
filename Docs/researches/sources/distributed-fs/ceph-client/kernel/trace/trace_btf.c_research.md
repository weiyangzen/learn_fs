# sources/distributed-fs/ceph-client/kernel/trace/trace_btf.c

## Purpose
`trace_btf.c` provides small BTF lookup helpers for trace probe argument parsing. It lets trace probe code find function prototypes, enumerate function parameters, and resolve struct/union members including members inside anonymous nested aggregates.

## Important APIs, types, and functions
The exported helpers are `btf_find_func_proto()`, `btf_get_func_param()`, and `btf_find_struct_member()`. Internal support includes `BTF_ANON_STACK_MAX` and `struct btf_anon_stack`, which tracks type IDs and accumulated offsets while walking anonymous nested structs/unions.

## Control flow
`btf_find_func_proto()` calls `bpf_find_btf_id()` for a function name, validates that the result is `BTF_KIND_FUNC`, follows its `type` to the corresponding `BTF_KIND_FUNC_PROTO`, and returns both the BTF object and type. On failure after acquiring BTF, it calls `btf_put()`. `btf_get_func_param()` validates that its input is a function prototype, sets the parameter count, and returns the parameter array or NULL for no parameters. `btf_find_struct_member()` allocates a fixed-depth stack, scans members by name, pushes anonymous aggregate members for later traversal, and returns the found member plus accumulated anonymous offset.

## State and persistence behavior
This file maintains no persistent global state. It acquires BTF references through the BPF/BTF core and transfers release responsibility to callers on success.

## Dependencies and integration points
It depends on `<linux/btf.h>`, BPF BTF ID lookup, slab allocation, and trace probe code that uses BTF context for typed fetch arguments. Cross-reference searches show use from `trace_probe.c` and trace output code.

## Risks
Callers must call `btf_put()` after successful `btf_find_func_proto()`. Anonymous aggregate traversal is bounded to 16 pending nodes; deeply nested anonymous structures beyond that limit may be missed. `btf_find_struct_member()` returns error pointers for invalid input or allocation failure, and callers must distinguish those from NULL not-found results.

## Test signals
Use fprobe/kprobe trace probe arguments that rely on BTF function parameters and nested struct members. Validate success paths, missing functions, non-prototype types, no-parameter functions, anonymous union/struct member offsets, and allocation-failure handling.
