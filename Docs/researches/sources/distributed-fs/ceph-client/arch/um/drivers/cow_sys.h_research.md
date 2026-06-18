<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h

Purpose: adapts generic COW image code to UML kernel/host helper services. It provides allocation, logging, string duplication, seek, size, and write wrappers used by `cow_user.c`.

Important APIs/types/functions: inline helpers are `cow_malloc()`, `cow_free()`, `cow_strdup()`, `cow_seek_file()`, `cow_file_size()`, and `cow_write_file()`. `cow_printf` maps to `printk`.

Control flow: COW code calls these wrappers instead of directly using allocator or OS helpers, keeping `cow_user.c` portable across UML build contexts.

State and persistence: no state is owned here; helper calls may query or write host files through `os_*` functions.

Dependencies and integration points: depends on `kern_util.h`, `os.h`, and `um_malloc.h`. It bridges the user-flavored COW code to UML kernel logging and memory helpers.

Risks: wrapper behavior affects storage image creation and parsing. Allocation flags must be safe in the call contexts where UBD opens/configures devices.

Test signals: compile COW helpers, run COW image create/read paths, and fault-inject allocation or host file size/seek/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h -->
