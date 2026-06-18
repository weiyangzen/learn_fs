<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h

**Purpose:** This small header exposes the SCLP line-mode tty driver pointer to related console code.

**Important APIs and types:** It declares `extern struct tty_driver *sclp_tty_driver;`.

**Control flow, state, and persistence:** The pointer is assigned by `sclp_tty_init()` after successful tty driver registration. `sclp_con.c` uses it in its console `.device` callback so printk's console device can resolve to the SCLP tty. Until initialization succeeds, the pointer remains null.

**Dependencies and integration:** It forward-depends on `struct tty_driver` from the tty core and is included by `sclp_con.c`.

**Risks and test signals:** Risks are limited but important for console integration: console device lookup before tty registration may return null, and failed tty init leaves the console without a tty backing device. Test signals include correct `/dev/ttyS0` association for the SCLP console and graceful behavior when `sclp_tty_init()` is skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.h -->
