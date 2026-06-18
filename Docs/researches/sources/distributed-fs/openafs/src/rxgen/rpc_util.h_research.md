## sources/distributed-fs/openafs/src/rxgen/rpc_util.h

### Purpose
`rpc_util.h` is the shared rxgen internal header tying scanner, parser, main program flags, and output emitters together.

### Important APIs, Types, And Functions
It defines allocation and printing macros, `struct rxgen_list`, `MAXLINESIZE`, externs for command-line flags and global parser/scanner state, list macros `STOREVAL`/`FINDVAL`, and prototypes for scanner, parser, utility, C-output, and header-output functions.

### Control Flow
No code executes here, but macro behavior affects control flow: `f_print` emits only when `scan_print` is true, and `alloc`/`ALLOC` directly call `malloc` without checking.

### State, Persistence, And Dependencies
The header exposes many mutable globals, including package/opcode state and function name arrays. It includes `rxgen_consts.h` and depends on `definition`, `relation`, `proc1_list`, `tok_kind`, and `token` from parser/scanner headers.

### Integration Points
Every rxgen source uses this as the common internal contract. It also declares `rpc_main.c` flags that select client, server, header, combined, stats, ANSI, ubik, and opcode behaviors.

### Risks
Broad global exposure makes ordering bugs easy and unit isolation hard. Allocation macros hide unchecked malloc calls. `f_print` as a conditional statement macro can be fragile in nested `if/else` contexts if used without braces.

### Test Signals
Build all rxgen output modes and run IDL fixtures under both `scan_print` enabled and disabled. Static analysis should flag unchecked allocations and macro misuse.
