# sources/distributed-fs/ceph-client/kernel/trace/trace_btf.h

## Purpose
`trace_btf.h` is the local declaration header for BTF helpers used by trace probe parsing and output code.

## Important APIs, types, and functions
It includes `<linux/btf.h>` and declares `btf_find_func_proto()`, `btf_get_func_param()`, and `btf_find_struct_member()`. The signatures expose BTF object lifetime transfer, function prototype parameter counts, and optional anonymous-member offset reporting.

## Control flow
The header has no runtime control flow. It gives other trace files access to the implementation in `trace_btf.c`.

## State and persistence behavior
No state is stored here. The declared APIs operate on BTF objects owned by the BTF core or returned with caller-managed references.

## Dependencies and integration points
Its only direct dependency is the kernel BTF type API. Integration points are trace probe parser code that maps user fetch expressions to typed kernel arguments and members.

## Risks
Because this header lacks include guards, duplicate inclusion in one translation unit would rely on identical prototype redeclaration being harmless. The prototypes also require callers to understand error-pointer versus NULL behavior documented in the C file.

## Test signals
Build coverage is the primary signal. Runtime signal comes from BTF-enabled trace probe tests that include this header through `trace_probe.c` or related files.
