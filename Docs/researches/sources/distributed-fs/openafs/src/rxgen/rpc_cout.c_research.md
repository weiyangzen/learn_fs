# sources/distributed-fs/openafs/src/rxgen/rpc_cout.c

## Purpose
`rpc_cout.c` emits C XDR routines for rxgen/rpcgen definitions and also builds per-parameter marshalling snippets used by RX client/server stub generation.

## Important APIs, Types, and Functions
- `emit()` dispatches by definition kind and writes `xdr_<type>` plus `xdrfree_<type>`.
- `print_ifstat()` is the central relation-aware emitter for pointers, vectors, arrays, aliases, strings, and opaque bytes.
- `emit_enum()`, `emit_union()`, `emit_struct()`, and `emit_typedef()` generate body code per data definition.
- `print_param()` builds `Proc_list->code` and `Proc_list->scode` marshalling expressions for procedure parameters.

## Control Flow
For normal data definitions, `emit()` prints a function header, emits per-field/per-arm XDR calls, then prints a success trailer. `print_ifstat()` selects the correct helper (`xdr_pointer`, `xdr_vector`, `xdr_array`, `xdr_string`, `xdr_bytes`, or direct alias call) and emits failure checks. Procedure-parameter generation mutates `Proc_list` metadata as it encounters arrays, strings, and indirect parameters.

## State and Persistence
The module writes generated C to global `fout` and mutates global rxgen structures such as `Proc_list`, `PerProcCounter`, `typedef_defined`, and `defined`. There is no standalone persistent state beyond generated files.

## Dependencies and Integration Points
Depends on parsed `definition`/`declaration` trees from `rpc_parse.h`, symbol lists from `rpc_util.h`, and global flags such as `brief_flag`, `hflag`, and `cflag`. Called from `rpc_main.c` output passes.

## Risks and Edge Cases
Generated code correctness depends on relation/type classification. Fixed local buffers for code snippets and type names assume generated strings fit. `print_param()` has special cases for strings and arrays that mutate parameter type/name, making ordering and global state important.

## Test Signals
Generate XDR code for structs, enums, unions with defaults, typedef arrays, fixed vectors, opaque arrays, and string parameters; compile generated output with strict warnings and run round-trip XDR tests.
