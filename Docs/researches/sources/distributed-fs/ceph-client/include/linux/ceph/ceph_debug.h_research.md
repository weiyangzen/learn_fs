## sources/distributed-fs/ceph-client/include/linux/ceph/ceph_debug.h

**Purpose:** This header defines Ceph-specific debug and client-context logging macros.

**Important APIs/types/functions:** It sets `pr_fmt` to prefix messages with `KBUILD_MODNAME`. `dout()` and `doutc()` expand differently depending on `CONFIG_CEPH_LIB_PRETTYDEBUG`, `DEBUG`, and dynamic debug: pretty mode adds filename/line and optional client FSID/global ID, otherwise it wraps `pr_debug`. Client-context macros include notice/info/warn/warn_once/err and ratelimited warn/err variants with `[fsid global_id]` prefixes.

**Control flow, state, persistence:** Logging calls evaluate through printk/dynamic-debug paths. In non-debug builds, some forms become `no_printk` to preserve format checking without emitting output. No persistent state is stored here.

**Dependencies/integration:** Depends on string basename helpers and Ceph client objects exposing `fsid` and `monc.auth->global_id`. Integrated across Ceph lib and filesystem/client code.

**Risks and test signals:** Risks include using `doutc()` before auth/client pointers are initialized, logging sensitive values, format-string mismatches hidden by config combinations, and excessive debug overhead in pretty mode. Test signals include dynamic-debug toggles, compile coverage with/without pretty debug, null/early-client path review, and ratelimited log behavior under repeated errors.
