# sources/distributed-fs/openafs/src/sys/Makefile.in

## Purpose
`src/sys/Makefile.in` builds the OpenAFS user-space syscall shim libraries, RMTSYS RPC support, exported syscall headers, and small inode-operation test utilities.

## Important APIs, types, and functions
Key targets are `libsys.a`, `liboafs_sys.la`, `libafsrpc_sys.la`, `libsys_pic.la`, `rmtsysd`, `depinstall`, `install`, `dest`, `generated`, and `tests`. Generated artifacts come from `rmtsys.xg` through `RXGEN`: `rmtsys.cs.c`, `rmtsys.ss.c`, `rmtsys.xdr.c`, `rmtsys.h`, and kernel variants `Krmtsys.*`.

## Control flow
The default `all` target builds libraries, daemon, headers, export files, and generated install-tree copies. Platform-specific cases select AIX export handling, real assembly syscall stubs for SGI/AIX/HP-UX, or a touched empty `syscall.c` elsewhere. Test programs compile individual tools such as `iinc`, `idec`, `icreate`, `iopen`, `iread`, `iwrite`, `istat`, and `fixit` against `LIBS`.

## State and persistence behavior
The makefile writes generated RX files, libtool archives, static archives, export stubs, component version files, installed headers under `TOP_INCDIR`, libraries under `TOP_LIBDIR`, and install/dest tree content. `clean` removes generated code, libraries, test binaries, syscall placeholders, and export files.

## Dependencies and integration points
It includes `Makefile.config`, `Makefile.lwp`, and `Makefile.lwptool`, links RX/LWP/OPR/roken/hcrypto support, uses `RXGEN`, libtool rules, install macros, and AIX export lists. It provides `liboafs_sys` to many higher-level OpenAFS tools and servers.

## Risks
Platform case logic is easy to regress because syscall glue differs sharply by AIX, SGI, HP-UX, and generic Unix. A typo or ordering change can produce archives missing `syscall.o` or AIX export data. Generated RX files must be in sync with `rmtsys.xg`, and clean rules are broad enough to remove all generated outputs.

## Test signals
Test by running `make generated`, `make libsys.a`, `make liboafs_sys.la`, and platform-specific `depinstall`/`install` dry runs where possible. On legacy platforms, verify `syscall.lo` and export-file selection; on generic Unix, verify the placeholder syscall object is harmless.
