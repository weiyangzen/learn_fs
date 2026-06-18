# sources/distributed-fs/openafs/src/rxgen/rpc_hout.c

## Purpose
`rpc_hout.c` emits C header declarations for rxgen/rpcgen data definitions and procedure prototypes.

## Important APIs, Types, and Functions
- `print_datadef()` dispatches definition emission and emits `xdr_`/`xdrfree_` prototypes for non-rxgen data definitions.
- `pstructdef()`, `puniondef()`, `penumdef()`, `ptypedef()`, and `pconstdef()` emit C type/constant declarations.
- `psprocdef()` and `psproc1()` emit client, split, multi, ubik, and server-prefixed procedure prototypes.
- `pdeclaration()` emits one declaration with relation-specific syntax.
- `undefined2()` decides whether to prefix forward references with `struct`.

## Control Flow
For every parsed definition, `print_datadef()` optionally suppresses scanner echo for server generation, dispatches to the right emitter, then writes XDR prototypes. Procedure definitions may emit Start/End split prototypes, normal client prototypes, ubik wrappers, and server-manager prototypes depending on global flags and definition metadata.

## State and Persistence
The module writes to global `fout` and records type metadata into global lists such as `uniondef_defined` and `typedef_defined`. It reads global flags including `Sflag`, `uflag`, `kflag`, `brief_flag`, and `ServerPrefix`.

## Dependencies and Integration Points
Called by `rpc_main.c` during header and server-stub passes. It depends on parser data structures and utility functions from rxgen.

## Risks and Edge Cases
Prototype generation is sensitive to parameter direction flags and `OUT_STRING` handling. Fixed-size local `prefix` buffers assume only small prefixes like `struct `. Brief-mode array layouts differ from normal mode, so generated C and XDR emitters must agree.

## Test Signals
Generate headers for structs, recursive unions, typedef arrays, strings, split/multi procedures, ubik mode, and server prefixes; compile both generated header and generated C stubs together.
