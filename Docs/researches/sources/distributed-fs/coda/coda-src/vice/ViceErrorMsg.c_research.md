# sources/distributed-fs/coda/coda-src/vice/ViceErrorMsg.c

`ViceErrorMsg.c` provides one small compatibility function, `ViceErrorMsg`, that converts Vice, RPC2, and Unix error codes into human-readable strings for server logging and diagnostics. Negative error codes are treated as RPC2 errors and delegated to `RPC2_ErrorMsg`. Non-negative values are matched against selected Vice volume and consistency errors, with unknown values falling back to `strerror`.

The explicit mappings include success, volume salvage required, bad vnode number, volume-not-online, volume-exists, no service, offline, already-online, and `EINCONS` as "Inconsistent Object". It depends on RPC2 headers for negative RPC error reporting and on `inconsist.h` for the Coda inconsistency error code. It returns `char *` for historical compatibility, although many returned strings are string literals or library-owned buffers.

Control flow is simple and side-effect free. There is no persistent state. Integration points include server files that log callback/bind failures and any code path that reports Vice or RPC errors to administrators. In this subset, `clientproc.cc` uses it when callback binding or callback checks fail.

Risks are mostly semantic: because unknown positive values use `strerror`, a Vice-specific positive error not listed here may be misreported as an unrelated errno string. The return type allows callers to assume mutability even though literals must not be modified. Thread-safety follows the behavior of `strerror` and `RPC2_ErrorMsg` on the target platform. Test signals include all explicit mappings, a negative RPC2 code, an ordinary errno such as `EPIPE`, and an unmapped positive Vice-like value to confirm fallback behavior.
