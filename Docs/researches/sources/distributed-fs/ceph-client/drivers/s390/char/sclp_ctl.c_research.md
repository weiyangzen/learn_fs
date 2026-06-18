<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c

**Purpose:** `sclp_ctl.c` provides a restricted misc ioctl interface at `/dev/sclp` for user space to submit selected raw SCCB command words.

**Important APIs and functions:** The only supported ioctl is `SCLP_CTL_SCCB`. `sclp_ctl_sccb_wlist[]` whitelists command words `0x00400002` and `0x00410002`. `sclp_ctl_ioctl_sccb()` copies a small user descriptor, validates the command, copies a page-sized user SCCB into DMA memory, validates the SCCB length field, submits a synchronous request, and copies the returned SCCB bytes back.

**Control flow, state, and persistence:** There is no persistent per-open state. The misc device is registered with `builtin_misc_device()`. Every ioctl allocates a zeroed DMA page and frees it before return.

**Dependencies and integration:** It depends on `asm/sclp_ctl.h` for the user ABI, the SCLP synchronous command API, miscdevice, and uaccess helpers.

**Risks and test signals:** Risks include exposing raw firmware calls, insufficient whitelist coverage or overly broad whitelist additions, user SCCB length validation bugs, and 64-bit user pointer conversion via `u64_to_uptr()`. Tests should cover unsupported command rejection, too-short copied SCCBs, invalid length greater than copied bytes, successful round trip with a mocked/valid command, and fault-injection for copy failures and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ctl.c -->
