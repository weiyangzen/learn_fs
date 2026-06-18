<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c

Purpose: Recoverable-address machine check exercise using VAS/NX mapping behavior. It intentionally maps a VAS paste address and probes that recoverable faults are surfaced as SIGBUS rather than killing unrelated state.

Important APIs and types: Defines `sigbus_handler`, `test_ra_error()`, and `main()`. Uses `VAS_TX_WIN_OPEN`, `struct vas_tx_win_open_attr`, `mmap`, `ioctl`, and `test_harness`.

Control flow: `test_ra_error()` opens `/dev/crypto/nx-gzip`, opens a VAS transmit window, maps the window, installs a SIGBUS handler, touches the mapped paste area to trigger the machine-check path, and validates that the expected fault was observed.

State and persistence: The only persistent state is the open/mapped device window during the test. `faulted` records signal delivery.

Dependencies and integration points: Depends on the local `vas-api.h`, `utils.h`, the NX gzip character device, VAS kernel support, and signal delivery.

Risks: The test requires privileged/platform-specific hardware support and will skip/fail differently depending on `/dev/crypto/nx-gzip` availability. Fault injection around accelerator mappings is architecture-sensitive.

Test signals: Pass means the kernel reports the recoverable access error through the expected signal path; absent device should lead to a skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mce/inject-ra-err.c -->
