<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c -->
# sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c

Purpose: Implements Hyper-V host-to-guest file copy service using the VMBus UIO channel for the fcopy integration component.

Important APIs/types/functions: `get_ring_buffer_size()` discovers channel ring size from sysfs. File operations are `hv_fcopy_create_file()`, `hv_copy_data()`, `hv_copy_finished()`, `hv_fcopy_start()`, and `hv_fcopy_send_data()`. Protocol negotiation uses `vmbus_prep_negotiate_resp()`. `fcopy_pkt_process()` parses incoming VMBus packets and sends responses through `rte_vmbus_chan_send()`. `fcopy_get_first_folder()` discovers UIO instance; `main()` daemonizes, maps rings, and runs the receive loop.

Control flow: On startup the daemon optionally forks, opens syslog, discovers ring size and UIO device, mmaps Tx/Rx rings, unmasks interrupts, then waits on `pread()` from `/dev/uio*`. Each notification receives a raw VMBus packet, handles negotiate or fcopy message, writes a response into the Tx ring, and signals the host by writing to the UIO fd.

State and persistence: Global state includes the packet buffer `desc`, current `target_fd`, `target_fname`, and `filesize`. Persistent side effects are files/directories created from host-supplied path/name and copy flags. It writes syslog records and keeps the daemon process running indefinitely.

Dependencies/integration: Depends on Hyper-V kernel UAPI (`linux/hyperv.h`), `vmbus_bufring` helpers, sysfs paths for the fcopy VMBus device UUID, `/dev/uio*`, locale/wide-character conversion, and syslog. It is installed only on x86/x86_64 by the Makefile.

Risks/tests: Risks include trusting host-supplied paths, limited UTF-16 conversion replacing non-ASCII with `X`, path creation by mutating `path_name`, target fd lifecycle if a copy aborts, race-prone first-folder discovery, and packet-length validation gaps beyond the fcopy header. Test signals are negotiation version match/mismatch, create/no-overwrite/create-path flags, writes with offsets, ENOSPC mapping, complete-copy close, UIO disconnect/error paths, foreground `--no-daemon`, and sysfs discovery retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_fcopy_uio_daemon.c -->
