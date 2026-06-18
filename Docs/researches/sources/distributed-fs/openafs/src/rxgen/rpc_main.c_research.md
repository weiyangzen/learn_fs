# sources/distributed-fs/openafs/src/rxgen/rpc_main.c

## Purpose
`rpc_main.c` is the top-level driver for `rxgen`, the OpenAFS RX protocol compiler. It parses command-line flags, preprocesses `.xg` input, and orchestrates generation of XDR, header, client stub, and server stub outputs.

## Important APIs, Types, and Functions
- `struct commandline` captures parsed flags and input/output paths.
- Global flags (`cflag`, `hflag`, `Cflag`, `Sflag`, `kflag`, `uflag`, `xflag`, `yflag`, `zflag`, `brief_flag`, etc.) drive scanner/parser and output modules.
- `main()` selects generation mode and invokes output passes.
- `extendfile()` computes output filenames.
- `open_input()` runs the C preprocessor with defines such as `-DRPC_XDR`, `-DRPC_HDR`, `-DRPC_CLIENT`, or `-DRPC_SERVER`.
- `c_output()`, `h_output()`, `C_output()`, and `S_output()` generate `.xdr.c`, `.h`, `.cs.c`, and `.ss.c` content.
- `parseargs()` validates flag combinations.

## Control Flow
`main()` allows `RXGEN_CPPCMD` to override the preprocessor, initializes parser state, parses flags, and either runs a single requested output pass or the default sequence. The default sequence regenerates parser state between passes and emits XDR, header, client, and server files; `-r` emits only client and server stubs. Each output pass opens preprocessed input, opens the target file, emits headers/includes, iterates `get_definition()`, and delegates to generation functions in other rxgen modules.

## State and Persistence
Persistent outputs are generated files and installed build-tool artifacts. Runtime state is broad and global: output file name buffers, include-dir list, parser state, package/function statistics, and output-mode flags. `record_open()` tracks files for cleanup on crash via utility code outside this subset.

## Dependencies and Integration Points
Depends on the C preprocessor, scanner/parser/util modules, `rpc_cout.c`, `rpc_hout.c`, and procedure-code generation functions from other rxgen files. Build integration comes from `rxgen/Makefile.in`, which injects `PATH_CPP`.

## Risks and Edge Cases
`open_input()` builds a shell command line for `popen`, so input/include paths with shell metacharacters are risky. Several filename buffers are fixed at 256 or 1024 bytes. `uppercase()` uses a static 100-byte buffer, so long include guards can overflow. Output would overwrite input is checked only for exact string equality after output filename selection.

## Test Signals
Run `rxgen` in each mode (`-c`, `-h`, `-C`, `-S`, `-r`, default) on representative `.xg` inputs; verify generated files compile and that cpp include handling, `RXGEN_CPPCMD`, `-I`, `-P`, `-o`, kernel mode, ubik mode, stats mode, and brief mode behave as expected.
