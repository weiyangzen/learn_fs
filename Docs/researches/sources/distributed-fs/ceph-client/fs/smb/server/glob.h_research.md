# sources/distributed-fs/ceph-client/fs/smb/server/glob.h

Purpose: provides server-local global definitions for KSMBD: debug categories, printk prefix formatting, Unicode length helper, and the default GFP allocation mask.

Important APIs/types/functions: `ksmbd_debug_types` is the external debug bitmask. Debug bits cover SMB, AUTH, VFS, OPLOCK, IPC, CONN, RDMA, and ALL. `ksmbd_debug(type, fmt, ...)` conditionally emits `pr_info()` when the corresponding bit is enabled. `UNICODE_LEN(x)` returns UTF-16 byte length for a character count. `KSMBD_DEFAULT_GFP` is `GFP_KERNEL | __GFP_RETRY_MAYFAIL`.

Control flow: server files include this header and call `ksmbd_debug()` in hot and error-adjacent paths. The macro compiles to a bit test plus `pr_info()` call, with `pr_fmt` adjusted to include `ksmbd` and optional submodule names.

State and persistence behavior: only the external debug mask is mutable runtime state. No persistent storage is defined.

Dependencies and integration points: includes character helpers, KSMBD Unicode and VFS cache headers, and Linux printk/GFP conventions through includers. It is one of the most widely included KSMBD local headers.

Risks: debug output can be noisy in hot paths if broad bits are enabled. `KSMBD_DEFAULT_GFP` may retry under memory pressure, so allocation sites using it must be able to sleep and tolerate latency. `UNICODE_LEN` assumes UTF-16 two-byte units and is not a complete conversion helper.

Test signals: build with different `SUBMOD_NAME` definitions, enable each debug category, run memory-pressure tests over request paths, and verify UTF-16 buffer sizing in auth/share/session code.
