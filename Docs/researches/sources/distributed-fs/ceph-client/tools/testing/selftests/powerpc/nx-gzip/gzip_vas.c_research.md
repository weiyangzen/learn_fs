<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c

Purpose: Shared VAS/NX submission backend for the gzip compressor and decompressor samples. It opens the accelerator, maps a paste window, submits CRBs with copy/paste instructions, waits for CSB completion, and faults in pages.

Important APIs and types: Defines `struct nx_handle`, `open_device_nodes`, `nx_function_begin`, `nx_function_end`, `nx_wait_for_csb`, `nxu_run_job`, `nxu_submit_job`, `nxu_sigsegv_handler`, and `nxu_touch_pages`.

Control flow: `nx_function_begin()` opens `/dev/crypto/nx-gzip`, issues `VAS_TX_WIN_OPEN`, maps the VAS window, and records the paste address. Job submission copies the CRB, pastes to the window, polls CSB validity with timebase/usleep backoff, handles fault-storage addresses from SIGSEGV, and returns NX completion code. `nx_function_end()` unmaps/closes/frees resources.

State and persistence: State is the heap `nx_handle`, mapped VAS page, file descriptor, and global `nx_fault_storage_address`. No durable state is stored.

Dependencies and integration points: Depends on local `vas-api.h`, `copy-paste.h`, `nxu.h`, `nx_dbg.h`, PPC timebase APIs, and the NX/VAS kernel driver.

Risks: Paste retry/poll loops can hang or run long on broken hardware. Signal-based fault recovery is specialized and assumes the test process owns the fault context.

Test signals: Successful compression/decompression jobs validate device open, VAS mapping, copy/paste instructions, CSB polling, and page touching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzip_vas.c -->
