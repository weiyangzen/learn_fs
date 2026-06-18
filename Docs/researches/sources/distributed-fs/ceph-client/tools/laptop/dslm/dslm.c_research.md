<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c -->
# sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c

Purpose: `dslm.c` is a simple disk sleep monitor that samples an ATA disk's power mode and prints time spent active, sleeping, or unknown until interrupted.

Important APIs/functions: `check_powermode()` issues `HDIO_DRIVE_CMD` with `WIN_CHECKPOWERMODE1`, retries `WIN_CHECKPOWERMODE2`, and maps results to active/sleeping/unknown. `state_name()` and `myctime()` format output. `measure()` samples once per second, detects state transitions, accumulates per-state durations, and prints summary percentages. `ender()` handles SIGINT by setting global `endit`. `main()` parses either `<disk>` or `-w <time> <disk>`-shaped arguments, opens the disk nonblocking read-only, waits for settle time, installs SIGINT, and calls `measure()`.

Control flow: after optional settle sleep, the loop calls `check_powermode()` every second. When the state changes or SIGINT ends the loop, it accounts elapsed time against the previous state and prints the transition.

State and persistence: runtime state is in local counters and global `endit`; no files are modified. The disk fd remains open until exit.

Dependencies/integration: depends on Linux `hdreg.h`, ATA ioctls, permissions to open the block device, and signal handling. It is standalone and built by the local Makefile.

Risks and test signals: notable risk: `if (!(fd = open(...)))` treats fd 0 as failure and negative fd as success; it should have been `fd < 0`. Other risks are deprecated ioctls, non-ATA devices, percentage divide by zero on very short runs, and `ctime()` buffer mutation. Test with invalid devices, fd 0 edge via closed stdin, SIGINT summary, and active/sleeping disks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c -->
