# sources/distributed-fs/lizardfs/src/common/errno_defs.h

Purpose: provides missing POSIX errno constants on Windows builds.

Important APIs/types/functions: defines `ENODATA`, `ENOTBLK`, `EDQUOT`, and `ETXTBSY` under `_WIN32`.

Control flow: preprocessor-only compatibility shim.

State and persistence: none.

Dependencies and integration: includes `platform.h`; used where cross-platform code references Unix errno names.

Risks: numeric values are compatibility choices and may not map to native Windows errors. Definitions are skipped on non-Windows platforms to avoid conflicts.

Test signals: no direct tests; build coverage on Windows is the main signal.
