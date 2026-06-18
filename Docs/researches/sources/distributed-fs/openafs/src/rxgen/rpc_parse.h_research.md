## sources/distributed-fs/openafs/src/rxgen/rpc_parse.h

### Purpose
`rpc_parse.h` defines the in-memory AST and procedure metadata used by rxgen parsing and generation.

### Important APIs, Types, And Functions
Core enums are `defkind` for definition/procedure component kinds and `relation` for alias, pointer, fixed vector, and variable array declarations. Important structures include `declaration`, `decl_list`, `enumval_list`, `case_list`, `typedef_def`, `struct_def`, `union_def`, `param_list`, `proc1_list`, `procedure_def`, `special_def`, `spec_list`, and top-level `definition`.

### Control Flow
The header has no executable flow, but its layout drives parser and generator decisions. `definition.def_kind` selects the active union member, while `definition.pc` is populated for procedures. `param_list.param_kind`, `param_flag`, and `procedure_def.paramtypes[IN/OUT/INOUT]` control marshal/unmarshal generation.

### State, Persistence, And Dependencies
Instances are allocated by parser helpers and stored in global `rxgen_list` chains. Procedure and declaration strings are scanner-owned heap allocations or string literals. The header assumes `char` flag fields can hold bitwise param flags such as `FREETHIS_PARAM` and `OUT_STRING`.

### Integration Points
`rpc_parse.c` creates these structures, `rpc_cout.c` and `rpc_hout.c` consume them for C/XDR/header output, and `rpc_util.c` inspects declarations for typedef/vector handling.

### Risks
The AST lacks ownership annotations, so freeing is intentionally minimal. `IN`, `OUT`, and `INOUT` macros are redefined in the header, which can surprise includers. Several fields are reused across definition kinds, so callers must honor `def_kind`.

### Test Signals
Compile coverage of every parser/generator object is the main signal. IDL tests should inspect generated output for correct relation handling, param flags, typedef expansion, and procedure direction counts.
