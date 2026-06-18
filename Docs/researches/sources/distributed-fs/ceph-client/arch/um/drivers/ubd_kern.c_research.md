<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c

Purpose: implements the UML block device driver (`ubd*`) and its helper-thread I/O engine. It maps guest block requests to host file I/O, supports read-only/sync/shared/no-COW/no-trim flags, copy-on-write images, discard/write-zeroes, dynamic mconsole config, and block-mq registration.

Important APIs/types/functions: key structs are `io_desc`, `io_thread_req`, `cow`, and `ubd`. Configuration/open helpers include `ubd_setup_common()`, `ubd_config()`, `ubd_add()`, `ubd_remove()`, `ubd_open_dev()`, `open_ubd_file()`, `create_cow_file()`, and `ubd_close_dev()`. I/O functions include `ubd_queue_rq()`, `ubd_submit_request()`, `ubd_alloc_req()`, `ubd_map_req()`, `cowify_req()`, `cowify_bitmap()`, `ubd_intr()`, `do_io()`, and `io_thread()`.

Control flow: boot or mconsole config parses `ubd<n><flags>=file[,backing][,serial]`, stores per-device config, and late init registers disks for configured entries, defaulting `ubd0` to `root_fs`. Opening detects COW headers, validates/switches backing files, reads COW bitmaps, opens backing read-only, and registers a block-mq disk. Queueing starts a block request, builds an `io_thread_req` with one descriptor per segment or special request, translates COW sector masks and bitmap updates, and writes the request pointer to the helper pipe. The helper reads pointers, performs pread/pwrite/fallocate/fsync against chosen host FD ranges, updates COW bitmap words, and writes completed pointers back. The IRQ handler completes block-mq requests.

State and persistence: persistent state lives in host disk image and COW files. Runtime state includes `ubd_devs[]`, open FDs, COW bitmap in vmalloc memory, platform devices, disks, tag sets, helper-thread pipe buffers, and remainder buffers for partial pipe reads.

Dependencies and integration points: depends on Linux block-mq, gendisk, platform devices, mconsole, UML IRQ/helper-thread/host file APIs, COW helpers, and generic block ioctls.

Risks: helper-thread code is explicitly outside normal kernel context and must not call kernel services. Pointer IPC and partial-read remainder handling are subtle. COW bitmap updates must stay consistent with data writes. Request completion frees allocated request wrappers; failure to write to the helper can leak or stall requests. `map_error()` expects positive errno inputs but callers sometimes pass negated return conventions, so error-code sign handling deserves tests.

Test signals: boot from `root_fs`, read/write block devices, read-only/sync/shared/no-trim flags, COW creation and backing mismatch/switching, discard/write-zeroes support disablement on `NOTSUPP`, flushes, HDIO identity/CDROM volume ioctls, mconsole add/remove while open/closed, helper-thread failure fallback, and high segment-count I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c -->
