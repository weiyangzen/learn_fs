<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c

Purpose: Table-driven tests for the `/dev/papr-vpd` Vital Product Data interface. It validates handle creation, reads, invalid inputs, rereads, and system location-code lookup.

Important APIs and types: Defines tests for open/close, all-VPD handle, byte-at-a-time reads, unterminated location code, NULL handle pointer, close-without-read, reread consistency, system location code, plus `get_system_loc_code`, `vpd_test` table, and `main()`.

Control flow: Each subtest opens `/dev/papr-vpd`, creates a read handle with `PAPR_VPD_IOC_CREATE_HANDLE`, reads via the returned fd, checks size/EOF/content containing `System VPD`, or verifies invalid inputs return `EINVAL`/`EFAULT`. System location code is derived from device-tree `model` and `system-id` files.

State and persistence: No persistent kernel state should change. It allocates buffers and opens transient fds for VPD handles.

Dependencies and integration points: Depends on `/dev/papr-vpd`, `<asm/papr-vpd.h>`, device-tree sysfs files, GNU `memmem`, and `utils.h` file helpers.

Risks: Platform VPD content and location-code formatting are firmware-dependent, so some subtests skip when data cannot be determined. The test assumes `System VPD` appears in returned blobs.

Test signals: Pass confirms stable PAPR VPD ioctl, read, EOF, and error handling semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_vpd/papr_vpd.c -->
