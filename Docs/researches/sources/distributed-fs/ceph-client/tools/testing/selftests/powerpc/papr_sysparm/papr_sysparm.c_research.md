<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c

Purpose: Exercises the `/dev/papr-sysparm` character-device ioctl ABI for reading and rejecting system parameters.

Important APIs and types: Defines tests `open_close`, `get_splpar`, `get_bad_parameter`, `check_efault_get`, `check_efault_set`, `set_hmc0`, `set_with_ro_fd`, the `sysparm_test` table, and `main()`.

Control flow: `main()` iterates table-driven subtests. The tests open the device, GET parameter 20, verify unsupported parameter leaves buffers unchanged, verify NULL pointers return `EFAULT`, and verify SET permission/read-only-fd errors are `EPERM` or `EBADF` with skips for unsupported firmware operations.

State and persistence: No persistent state is changed; attempted SETs target non-settable HMC0 and are expected to fail.

Dependencies and integration points: Depends on `/dev/papr-sysparm`, `<asm/papr-sysparm.h>`, errno semantics, and `utils.h`.

Risks: Firmware may not support SET, producing skips. Error-code expectations are part of the ABI and should be changed only with kernel/userspace contract updates.

Test signals: Pass means the sysparm device handles valid GETs and rejects invalid operations with stable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_sysparm/papr_sysparm.c -->
