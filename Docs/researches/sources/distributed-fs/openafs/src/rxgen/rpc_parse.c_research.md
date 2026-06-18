## sources/distributed-fs/openafs/src/rxgen/rpc_parse.c

### Purpose
`rpc_parse.c` is the rxgen parser and procedure stub generator. It parses SunRPC/RXGEN IDL definitions, tracks package/opcode/stat metadata, and emits client stubs, server stubs, ubik callback wrappers, multi-call macros, opcode dispatch tables, and header statistics through shared `fout`.

### Important APIs, Types, And Functions
The public entry points are `get_definition()`, `er_Proc_CodeGeneration()`, `h_Proc_CodeGeneration()`, `h_opcode_stats()`, `generate_multi_macros()`, `IsRxgenToken()`, and `IsRxgenDefinition()`. Most work is in static helpers such as `def_struct`, `def_union`, `def_typedef`, `def_package`, `check_proc`, `analyze_ProcParams`, `cs_Proc_CodeGeneration`, `ss_Proc_CodeGeneration`, and opcode-dispatch emitters. It fills the AST types declared in `rpc_parse.h` and uses scanner tokens from `rpc_scan.c`.

### Control Flow
`get_definition()` reads the next token, dispatches to a definition parser, scans the terminating semicolon for ordinary RPCL definitions, and records definitions in global lists. Procedure parsing requires an active package, parses direction-tagged params, assigns or auto-increments opcodes, updates package/master opcode ranges, emits code immediately according to flags, records procedure metadata for later dispatch generation, and updates statistics arrays. Split and multi procedures temporarily hide IN or OUT params while emitting Start/End forms.

### State, Persistence, And Dependencies
The file is heavily stateful: package index, prefixes, opcode ranges, procedure lists, special typedef lists, function name arrays, stat indices, and split prefixes are globals reset by `reinitialize()` in `rpc_util.c`. Persistent output is generated C/header text written to `fout`. Dependencies include `rpc_scan` token routines, `rpc_util` allocation/error/list helpers, and `rpc_cout.c`/`rpc_hout.c` callbacks for XDR data and parameter-code generation.

### Integration Points
`rpc_main.c` drives this parser while selecting output modes with `Sflag`, `Cflag`, `hflag`, `cflag`, `uflag`, `xflag`, and related globals. Generated stubs integrate with Rx calls, XDR streams, rxgen error constants, ubik clients, rx statistics, and `rx_multi.h`.

### Risks
Fixed-size buffers and counters (`MAX_PACKAGES`, `MAX_FUNCTION_NAME_LEN`, function arrays, local 100/150/250-byte buffers) are central risk points. The parser interleaves parsing and code emission, so error recovery is impossible and global state ordering matters. Opcode auto-assignment forbids later explicit assignments, and old-style dispatch is selected when opcode holes exist. Memory is mostly process-lifetime allocation with limited frees because rxgen exits after generation.

### Test Signals
Useful tests include IDL fixtures for structs, unions, typedef aliases, variable arrays, strings, packages, explicit and implicit opcodes, opcode holes, split and multi procedures, ubik output, custom/special declarations, stats output, and boundary failures for long function names or too many packages/functions.
