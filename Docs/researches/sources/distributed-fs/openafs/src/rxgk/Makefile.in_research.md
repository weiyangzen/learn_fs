## sources/distributed-fs/openafs/src/rxgk/Makefile.in

### Purpose
`rxgk/Makefile.in` builds and installs the rxgk security library, generated RPC stubs, generated error table, and public headers.

### Important APIs, Types, And Functions
Primary targets are `all`, `generated`, `depinstall`, `liboafs_rxgk.la`, `librxgk_pic.la`, `install`, `dest`, and `clean`. Generated artifacts come from `rxgk_int.xg` via `RXGEN` and `rxgk_errs.et` via `COMPILE_ET`.

### Control Flow
The default build installs headers into `TOP_INCDIR`, generates client/server/XDR/header files with `RXGEN -b -A -x`, compiles listed libtool objects, and links shared and PIC libraries against `opr`, `comerr`, `rx`, and RFC3961 crypto.

### State, Persistence, And Dependencies
Persistent outputs include generated `.cs.c`, `.ss.c`, `.xdr.c`, `rxgk_int.h`, `rxgk_errs.[ch]`, installed headers, and libtool libraries. Installation is conditional on `@ENABLE_RXGK@`.

### Integration Points
The makefile connects rxgk C sources to rxgen and comerr-generated protocol material. Public include users get `rxgk.h`, `rxgk_types.h`, `rxgk_errs.h`, and `rxgk_int.h`.

### Risks
`LT_libs` has a placeholder comment for future GSSAPI linkage, matching unimplemented GSS procedures. Clean removes generated RPC files but not every installed artifact. Conditional install means builds can produce libraries while packaging may skip headers if rxgk is disabled.

### Test Signals
Signals include clean-tree build, generated-file rebuild after `.xg` or `.et` changes, `ENABLE_RXGK` install/dest behavior, symbol export validation with `liboafs_rxgk.la.sym`, and dependency tracking for generated headers.
