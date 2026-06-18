# sources/distributed-fs/ceph-client/drivers/s390/char/vmur.h

Purpose: private declarations and constants for the z/VM unit-record character driver.

Important APIs/types/functions: defines VM unit-record class constants, supported default device types, packed `struct file_control_block`, spool-file status flags, `struct urdev`, `struct urfile`, minor/count limits, `MAX_RECS_PER_IO`, write command opcode, debug macro `TRACE`, ccw id helper `CCWDEV_CU_DI`, and `FILE_RECLEN_OFFSET`.

Control flow: no executable flow; structures are consumed by `vmur.c` for diagnose file metadata, ccw device state, and per-open state.

State and persistence: `urdev` persists for each probed ccw unit-record device while present; `urfile` is per open. VM spool file metadata in `file_control_block` is read from CP and not stored persistently by Linux.

Dependencies and integration: includes Linux refcount/workqueue and expects ccw, cdev, completion, mutex, waitqueue, and device definitions from implementation includes.

Risks: packed FCB layout and `FILE_RECLEN_OFFSET` are ABI-sensitive to z/VM spool page format; direct minor-to-devno mapping consumes a large minor range; record count limit protects channel program size.

Test signals: compile with `vmur.c`, FCB parsing for held/in-use/CP dump files, supported 2540/1403 device matching, and write count capping to 511 records.
