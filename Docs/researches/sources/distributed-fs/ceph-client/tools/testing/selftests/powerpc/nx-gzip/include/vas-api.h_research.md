<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h

Purpose: Local VAS ioctl ABI copy for NX gzip selftests. It lets the tests open a transmit window without depending on installed kernel headers.

Important APIs and types: Defines `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr`.

Control flow: No executable flow. `gzip_vas.c` fills the struct and issues the ioctl before mapping the paste window.

State and persistence: No direct state; ioctl success creates kernel VAS state associated with the file descriptor.

Dependencies and integration points: Depends on Linux type/ioctl headers and must match the kernel VAS uAPI.

Risks: Header drift from the kernel ABI breaks accelerator open or silently changes attributes.

Test signals: Successful `nx_function_begin()` is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/vas-api.h -->
