# sources/distributed-fs/ceph-client/tools/crypto/ccp/Makefile

Purpose: Builds the AMD Dynamic Boost Control C shim as `dbc_library.so` for Python ctypes clients.

Important APIs, types, and functions: Sets UAPI include flags, target name, `all`, shared library rule from `dbc.c`, removes executable bit, and `clean`.

Control flow: `make` compiles `dbc.c` with `$(CC) $(CFLAGS) $(LDFLAGS) -shared` to `dbc_library.so` and `chmod -x` on the result.

State and persistence: Creates `dbc_library.so` in the current directory.

Dependencies and integration points: Depends on `include/uapi/linux/psp-dbc.h` and is loaded by `dbc.py` via `ctypes.CDLL("./dbc_library.so")`.

Risks: Does not pass `-fPIC`; platform/toolchain defaults determine whether shared build succeeds. Relative library location must match Python working directory.

Test signals: `make`, import `dbc.py` from the same directory, and `make clean`.
