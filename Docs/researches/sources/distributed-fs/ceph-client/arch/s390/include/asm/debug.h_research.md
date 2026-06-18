<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h

Purpose: Declares the s390 debug feature (`s390dbf`) ring-buffer API and early static debug support.

Important APIs/types/functions: `debug_info_t`, `debug_entry_t`, `debug_view`, register/unregister/view APIs, event/exception helpers, sprintf helpers, dump, level control, and `DEFINE_STATIC_DEBUG_INFO()`. Source-visible declarations include: #define _ASM_S390_DEBUG_H; #define DEBUG_MAX_LEVEL 6 /* debug levels range from 0 to 6 */; #define DEBUG_OFF_LEVEL -1 /* level where debug is switched off */; #define DEBUG_FLUSH_ALL -1 /* parameter to flush all areas */; #define DEBUG_MAX_VIEWS 10 /* max number of views in proc fs */; #define DEBUG_MAX_NAME_LEN 64 /* max length for a debugfs file name */; #define DEBUG_DEFAULT_LEVEL 3 /* initial debug level */; #define DEBUG_DIR_ROOT "s390dbf" /* name of debug root directory in proc fs */; #define DEBUG_DATA(entry) (char *)(entry + 1) /* data is stored behind */; #define __DEBUG_FEATURE_VERSION 3 /* version of debug feature */.

Control flow: Callers register debug areas and views, log level-filtered events into active ring areas, optionally switch areas on exceptions, and expose formatted output through debugfs/proc-style views.

State and persistence behavior: Persistent state includes per-debug-area ring pages, active page/entry indices, views, dentry handles, locks, levels, and early static buffers later replaced during init.

Dependencies and integration points: Direct includes are #include <linux/string.h>, #include <linux/spinlock.h>, #include <linux/kernel.h>, #include <linux/time.h>, #include <linux/refcount.h>, #include <linux/fs.h>, #include <linux/init.h>. Integrated with Integrates many s390 drivers, debugfs, early boot tracing, panic/critical paths, and documentation-defined formatting views..

Risks: `%s` sprintf entries store pointers rather than copying strings; lifetimes matter. Ring sizing, refcounts, and static registration must avoid use-after-free and lost diagnostic data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 499 lines, 14707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h -->
