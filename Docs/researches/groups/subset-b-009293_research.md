# subset-b-009293 research

Grouped research report for LTP filesystem and syscall tests under `sources/test-tools/ltp/testcases/kernel`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer.sh

Purpose: top-level filesystem race stress harness that creates `$TMPDIR/race`, starts many background worker scripts, lets them mutate/list the same small namespace for a requested duration, then kills workers and removes the tree. Important APIs and commands are shell `getopts`, `sleep`, background execution, `killall`, and `rm -rf`; integration is entirely through sibling `fs_racer_*` scripts in the same directory. Control flow only runs when `-t DURATION` is supplied: `execute_test` launches three instances each of create, directory-create, rename, hard/symlink, symlink, concat, list, and remove loops, then `call_exit` performs cleanup. State is persistent filesystem state in `$TMPDIR/race`, intentionally unstable because files, directories, links, and reads race each other. Risks are unquoted paths, process-wide `killall` matching by script name, and destructive cleanup of `$DIR`; test signal is survival without filesystem/kernel failure during the timed run.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_create.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_create.sh

Purpose: background mutator that repeatedly creates nested directories and writes a leaf file under a random numeric name. It takes `DIR` and `MAX`, chooses `file=$RANDOM%MAX`, runs `mkdir -p $DIR/$file/$file/`, then redirects `asdf` into `$DIR/$file/$file/$file`. Dependencies are Bash, `$RANDOM`, `mkdir`, and shell redirection; it is intended to run concurrently with removal, rename, concat, and link scripts launched by `fs_racer.sh`. State is the evolving nested directory/file layout beneath the shared race directory. Errors are redirected to `/dev/null` so expected races do not fail the script; kernel crashes, hangs, or filesystem corruption are the meaningful test signals. Risks include unquoted paths and an infinite loop that must be externally killed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_create.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_test.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_test.sh

Purpose: standalone deep-directory stress helper that repeatedly appends `/a` to an internal path, creates `race/$dir`, increments a counter, and prints the depth. It does not take the same `DIR`/`MAX` contract as the other racer helpers and is not launched by `fs_racer.sh`, so it appears to be an older/manual depth-growth probe. APIs are Bash looping, string concatenation, `mkdir`, arithmetic expansion, and `echo`. State is an ever-deepening path under a relative `race` directory, which exercises pathname length, directory creation, and lookup behavior. Risks are unbounded path growth and no cleanup; test signal is whether directory creation eventually fails cleanly rather than destabilizing the filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_dir_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_concat.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_concat.sh

Purpose: repeated read/append mutator for the racer workload. It takes `DIR` and `MAX`, chooses a random source and destination numeric name, then appends both `$DIR/$file` and `$DIR/$file/$file/$file` into `$DIR/$new_file`. Dependencies are Bash, `$RANDOM`, `cat`, and append redirection; it integrates with file and directory creators for its inputs and with removers/renamers that may delete paths during reads. State behavior is intentionally racy growth or replacement of destination files. Errors are suppressed because missing files, directories, and changing file types are expected. Risks include unbounded file growth, unquoted paths, and infinite execution; the signal is kernel/filesystem robustness during concurrent append/read/name changes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_concat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_create.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_create.sh

Purpose: repeated creator/writer that overwrites a random numeric file with zero-filled data. It takes `DIR` and `MAX`, computes a random `SIZE` up to `MAX_SIZE` using `$RANDOM`, prints it, and runs `dd if=/dev/zero of=$DIR/$file bs=1k count=$SIZE`. Dependencies are Bash, `dd`, `/dev/zero`, and the parent harness. State is file contents and allocated blocks in the shared race directory; other workers may remove, rename, link, or read these names during writes. Errors from `dd` are suppressed but size output remains noisy. Risks are large writes, disk pressure, unquoted paths, and an infinite loop; the pass signal is lack of filesystem/kernel failure under concurrent creation and truncation pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_create.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_link.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_link.sh

Purpose: repeated link mutator for adjacent numeric names. It takes `DIR` and `MAX`, computes `new_file=(file+1)%MAX`, then attempts both `ln -s $file $DIR/$new_file` and `ln $file $DIR/$new_file`. Dependencies are Bash and `ln`; the hard-link command uses a relative source name rather than `$DIR/$file`, so its behavior depends on current directory and is likely to fail in many runs. State is directory entries that may become symlinks, hard links, or fail due to preexisting paths. Errors are suppressed to tolerate races and invalid link attempts. Risks are ambiguous path handling and infinite execution; test signal is kernel/filesystem stability around link creation racing with unlink/rename/write.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_link.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_list.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_list.sh

Purpose: directory traversal pressure worker. It takes `DIR`, repeatedly starts ten concurrent `ls -R $DIR/` processes with output and errors redirected away, waits for them, then sleeps one second. Dependencies are Bash, `ls`, background jobs, and `wait`; the unused `MAX` assignment is harmless. State is read-only from this script, but it observes a namespace being mutated by the other racer workers. Risks are high process churn, unquoted paths, and indefinite execution. Test signal is absence of hangs, crashes, or traversal pathologies when recursive listing races with create, remove, rename, and link operations.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_list.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rename.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rename.sh

Purpose: repeated rename/replacement mutator. It takes `DIR` and `MAX`, chooses a random numeric name, computes the next numeric name as destination, and runs `mv -f $DIR/$file $DIR/$new_file` forever. Dependencies are Bash and `mv`; integration is with creator/remover/linker scripts sharing the same name pool. State changes are namespace-level renames that may overwrite or move files, directories, and links. Errors are suppressed because missing paths and incompatible file types are expected under race. Risks are unquoted paths and infinite operation; the meaningful signal is filesystem correctness under concurrent rename with reads, writes, links, and recursive listing.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rm.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rm.sh

Purpose: repeated deletion mutator for the racer workload. It takes `DIR` and `MAX`, chooses a random numeric entry, runs `rm -rf $DIR/$file`, suppresses errors, then sleeps one second. Dependencies are Bash and `rm`; integration is with all other racer helpers because it removes files, directories, and links they may currently use. State behavior is destructive namespace pruning under active access. Risks are the normal hazards of unquoted `rm -rf`, external kill requirement, and removal of paths while other tools hold descriptors. Test signal is kernel/filesystem resilience to concurrent recursive deletion and recreation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_rm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_symlink.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_symlink.sh

Purpose: symlink-specific namespace mutator. It takes `DIR` and `MAX`, chooses adjacent numeric names, then attempts symlinks from the destination to both a top-level numeric source and a nested `$file/$file/$file` source. Dependencies are Bash and `ln -s`; it integrates with directory creation, deletion, listing, concat, and rename workers. State is a changing set of symlink directory entries that may point to files, directories, or nonexistent targets. Errors are expected and suppressed when destinations already exist or vanish. Risks are infinite operation and unquoted paths; pass/fail signal is lack of filesystem/kernel instability while symlink resolution and directory changes race.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/racer/fs_racer_file_symlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/read_all/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/read_all/Makefile

Purpose: LTP leaf Makefile for the `read_all` filesystem exerciser. It sets `top_srcdir`, includes `include/mk/testcases.mk`, adds `_GNU_SOURCE` and `-pthread` to `CFLAGS`, links `read_all` with `-lrt`, and includes `generic_leaf_target.mk`. Dependencies are the LTP make infrastructure, pthreads for worker processes/IPC support, and realtime clock symbols used by the test. State is build-only; no runtime files are created here. Risks are missing pthread or librt settings causing link failures. Test signal is successful compilation of `read_all.c` into the LTP testcase binary.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/read_all/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/read_all/read_all.c -->
# sources/test-tools/ltp/testcases/kernel/fs/read_all/read_all.c

Purpose: recursively reads a small buffer from every non-symlink file under a user-specified directory, mainly to stress file-like kernel interfaces such as procfs, sysfs, and debugfs for crashes or severe errors. Important types/functions are `struct queue` in shared anonymous mmap, `struct worker`, `queue_push/pop`, `spawn_workers`, `read_test`, `visit_dir`, `sched_work`, timeout/restart helpers, and LTP options `-d`, `-r`, `-w`, `-W`, `-p`, `-t`, `-v`, `-q`, `-e`. Control flow parses options, computes worker count from CPU count unless overridden, forks worker processes with shared queues, recursively scans the tree, schedules each readable path `reads` times, then sends stop records and reaps children. State includes shared-memory queues, semaphores, worker heartbeat timestamps, child processes, and optional dropped privileges to nobody; persistent filesystem state is only read. Dependencies include LTP atomics, safe clock/test helpers, `fnmatch` extended patterns, POSIX semaphores, fork/wait, and directory traversal APIs. Risks are intentionally tolerated open/read errors, queue-full stalls, worker hangs on blocking kernel files, and path truncation limits; test signals are timeout restarts, info logs for problematic files, child exit health, and final `TPASS` after traversal completes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/read_all/read_all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/squashfs/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/squashfs/Makefile

Purpose: LTP leaf Makefile for SquashFS filesystem regression tests. It sets `top_srcdir`, includes `testcases.mk`, and delegates target generation to `generic_leaf_target.mk`. There are no custom compiler flags or libraries; build behavior is inherited from LTP. Runtime dependencies such as `mksquashfs`, root, a block device, and kernel config are declared in `squashfs01.c`, not the Makefile. State is build metadata only. Risk is minimal: incorrect `top_srcdir` would break includes, and missing LTP make infrastructure would prevent target discovery.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/squashfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/squashfs/squashfs01.c -->
# sources/test-tools/ltp/testcases/kernel/fs/squashfs/squashfs01.c

Purpose: regression test for SquashFS sanity-check fixes around full inode lookup, id lookup, and xattr blocks. `setup` creates 2048 files in `data`, assigns unique uid/gid pairs, sets `security.x` xattrs, runs `mksquashfs` with compression disabled into the LTP test device, and creates `mnt`; `run` mounts the device as `squashfs`, unmounts it, and reports success. Important APIs are `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_FCHOWN`, `SAFE_FSETXATTR`, `tst_cmd`, `mount`, and `SAFE_UMOUNT`. State includes generated source data, a SquashFS image on `tst_device->dev`, mount state tracked by `mounted`, and cleanup unmounting. Dependencies are root, a test block device, `mksquashfs`, `CONFIG_SQUASHFS`, and xattr support. Risks are environmental filesystem/xattr constraints and mount failures; test signal is successful mount/unmount, tagged to fixes `c1b2028315c` and `8b44ca2b634`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/squashfs/squashfs01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/Makefile

Purpose: LTP leaf Makefile for stdio stream behavior tests. It sets `top_srcdir`, includes the standard `testcases.mk`, and then `generic_leaf_target.mk`; no test-specific libraries or flags are added. The file integrates the five `stream0*.c` test programs into the LTP build system. State is build-only, with runtime tmpdir requirements declared in each C file. Risks are limited to LTP make include path correctness. Test signal is successful discovery and compilation of the stream testcase binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream01.c -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/stream01.c

Purpose: verifies `freopen()` redirects an existing stream to a new named file. The test opens `ltp_file1.txt`, writes `abc`, reopens the same `FILE *` onto `ltp_file2.txt`, writes `def`, closes, then reads both files through `read_file` and checks exact contents with `TST_EXP_EQ_STRN`. Important APIs are `SAFE_FOPEN`, `SAFE_FWRITE`, `SAFE_FREOPEN`, `SAFE_FREAD`, and `SAFE_FCLOSE`. State consists of two temporary files removed at the end of `run`. Dependencies are LTP safe stdio wrappers and a temporary directory. Risks are append-mode interactions if cleanup failed from a prior run; test signal is that first and second buffers land in different files as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream02.c -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/stream02.c

Purpose: checks that a FIFO created with `mknod()` can be opened by `fopen()` in `r+`, `w+`, and `a+` modes. `run` creates `ltp_file_node` as `S_IFIFO | 0666`, loops over mode strings, expects `fopen` to return non-NULL, closes successful streams, and unlinks the FIFO. Important APIs are `SAFE_MKNOD`, `fopen`, `TST_EXP_PASS_PTR_NULL`, and `SAFE_FCLOSE`. State is one temporary FIFO. Dependencies are tmpdir support and filesystem FIFO support. Risks are blocking semantics for FIFOs on unusual libc/filesystem combinations; test signal is pass for all modes without unexpected NULL stream.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream03.c -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/stream03.c

Purpose: validates `ftell()` after writes, rewind, relative seek, end seek, start seek, and reading to EOF. Setup copies random LTP data into a 30-byte buffer; `run` writes it to `ltp_file`, checks offsets 0, 30, 0, 10, 30, 0, and 30 after `fgets` drains the file. Important APIs are `SAFE_FOPEN`, `SAFE_FWRITE`, `SAFE_FTELL`, `SAFE_FSEEK`, `rewind`, and `fgets`. State is a temporary file and allocated buffers declared in `.bufs`. Dependencies are LTP random data and safe stdio wrappers. Risks are off-by-one expectations around append/update mode and null bytes in random data; test signal is exact offset matches through `TST_EXP_EQ_LI`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream04.c -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/stream04.c

Purpose: confirms `fwrite()` writes all bytes and `fread()` returns the same data. Setup copies the alphabet string into a buffer; `run` opens `ltp_file` in append/update mode, writes `DATASIZE` bytes, closes, reopens in read/update mode, reads the same byte count, unlinks, and compares buffers. Important APIs are `fwrite`, `fread`, LTP safe stdio wrappers, and `TST_EXP_EQ_STRN`. State is one temporary regular file plus allocated buffers. Dependencies are tmpdir and standard stdio behavior. Risks include `DATASIZE` including the string terminator due to `sizeof(DATA)`; the test intentionally compares that exact size. Test signal is full byte-count and matching buffer contents.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream05.c -->
# sources/test-tools/ltp/testcases/kernel/fs/stream/stream05.c

Purpose: verifies interaction between a `FILE *` stream and its underlying file descriptor returned by `fileno()`. `run` writes three random bytes through stdio, flushes, obtains the fd, writes the same bytes through `write`, fsyncs, seeks, reads back six bytes via the fd, checks both copies, then closes the fd and expects `fclose(stream)` to fail with `EBADF`. Important APIs are `SAFE_FILENO`, `SAFE_WRITE`, `SAFE_FSYNC`, `SAFE_FSEEK`, `SAFE_READ`, `SAFE_CLOSE`, and `TST_EXP_FAIL`. State is one temporary file and two buffers. Dependencies are tmpdir and LTP safe wrappers. Risks are mixing buffered stdio and descriptor I/O, which is the point of the test; pass signal is duplicated data and `EBADF` from final `fclose`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/stream/stream05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/Makefile

Purpose: trunk Makefile that integrates syscall subdirectories into the LTP build. It sets `top_srcdir`, includes `env_pre.mk`, filters out `profil` on uClibc, and filters many unsupported syscall directories on Android before including `generic_trunk_target.mk`. Important variables are `FILTER_OUT_DIRS`, `UCLIBC`, and `ANDROID`. State is build traversal configuration only; no runtime test state exists here. Dependencies are the LTP make framework and platform detection variables. Risks are platform-specific coverage gaps if filters are stale; test signal is correct recursive build selection for syscall suites.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/abort/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/abort/Makefile

Purpose: LTP leaf Makefile for abort syscall/libc behavior tests. It includes standard `testcases.mk` and `generic_leaf_target.mk` without custom flags or libraries. Runtime needs such as tmpdir, fork, and core limit setup are declared in `abort01.c`. State is build-only. Risks are minimal and limited to make include path correctness. Test signal is successful build of `abort01`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/abort/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/abort/abort01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/abort/abort01.c

Purpose: checks that `abort()` terminates a child with `SIGIOT` and produces a core dump. Setup raises `RLIMIT_CORE` to at least 512 KiB if possible; `verify_abort` forks, the child calls `abort`, and the parent checks `WIFSIGNALED`, `WCOREDUMP`, and `WTERMSIG`. Important APIs are `SAFE_FORK`, `SAFE_WAIT`, `abort`, `getrlimit`, `setrlimit`, and wait-status macros. State includes only process state and core-limit settings in a tmpdir. Dependencies are fork support and core dumps not disabled by hard limits; non-root cannot raise too-low hard limits. Risks include system core dump policy masking the core signal. Test signals are separate pass/fail reports for core dump and `SIGIOT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/abort/abort01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept/Makefile

Purpose: LTP leaf Makefile for `accept()` tests. It includes the standard LTP testcase and leaf target makefiles, and adds `-pthread` only for `accept02`, which uses server/client pthreads and checkpoints. Runtime socket setup is in the C files. State is build-only. Dependencies are pthread support for the CVE regression test. Risk is missing the target-specific flag causing unresolved pthread symbols. Test signal is successful build of `accept01`, `accept02`, and `accept03`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept01.c

Purpose: verifies `accept()` returns expected errno values for invalid descriptors, invalid address/length arguments, no queued connections, and datagram sockets. Setup creates and binds an IPv4 stream socket and UDP socket; `tcases` drive EBADF, EINVAL, and EOPNOTSUPP expectations through `TST_EXP_FAIL2`. Important APIs are `socket`, `bind`, `accept`, `SAFE_SOCKET`, and `SAFE_BIND`. State consists of two bound sockets and sockaddr buffers. Dependencies are IPv4 sockets. Risks include expected errno variation for bad userspace address on some architectures; the file encodes LTP's current expected behavior. Test signal is exact errno match per testcase.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept02.c

Purpose: CVE-2017-8890 regression test ensuring multicast group membership is not copied from a listening socket to the accepted socket. Setup allocates sockaddr/group structures, chooses an unused local TCP port, and builds a multicast `group_req`; `run` starts a server thread, waits for listen readiness, then starts a client thread. The server joins a multicast group, binds/listens/accepts, tries `MCAST_LEAVE_GROUP` on the accepted clone, and expects `EADDRNOTAVAIL`. Important APIs are `setsockopt` with `MCAST_JOIN_GROUP`/`MCAST_LEAVE_GROUP`, `accept`, pthreads, LTP checkpoints, and safe networking helpers. State includes three sockets and multicast membership only on the listening socket. Dependencies are IPv4 multicast socket options and pthreads. Risks are explicitly high on vulnerable kernels because the bug can destabilize the system; pass signal is failure to leave a group on the clone.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept03.c

Purpose: checks `accept()` error behavior over LTP's generic file descriptor corpus. `TST_FD_FOREACH` supplies many descriptor types; socket descriptors are skipped, `open_tree` and `O_PATH` descriptors expect `EBADF`, and other non-sockets expect `ENOTSOCK`. Important APIs are `TST_FD_FOREACH`, `tst_fd_desc`, and `accept`. State is the descriptor set created by the LTP fd iterator; no persistent filesystem state is owned by the file. Dependencies are LTP fd helpers and IPv4 sockaddr structures. Risks are kernel-specific errno differences for descriptor classes; test signal is exact `EBADF` or `ENOTSOCK` matching.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept/accept03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept4/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept4/Makefile

Purpose: LTP leaf Makefile for `accept4()` tests. It includes the standard testcase and generic leaf makefiles without custom flags. Runtime variants in `accept4_01.c` cover libc, direct syscall, and legacy `socketcall` where available. State is build-only. Risks are minimal unless platform syscall headers lack accept4/socketcall definitions handled by lapi. Test signal is successful compilation of the leaf target.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept4/accept4_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/accept4/accept4_01.c

Purpose: verifies that `accept4()` accepts connections and applies `SOCK_CLOEXEC` and `SOCK_NONBLOCK` flags correctly across syscall variants. Setup creates a listening IPv4 TCP socket, resolves its loopback connect address, and records the active variant; each testcase connects a client, calls libc `accept4`, direct `__NR_accept4`, or `socketcall(SYS_ACCEPT4)`, then checks `FD_CLOEXEC` via `F_GETFD` and `O_NONBLOCK` via `F_GETFL`. Important APIs are `accept4`, `tst_syscall`, `socketcall`, `connect`, `fcntl`, and safe socket helpers. State includes a persistent listening socket plus per-test accepted/client fds. Dependencies are IPv4 loopback and platform syscall support. Risks are variant availability and flag propagation regressions; test signal is exact match of close-on-exec and nonblocking bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/accept4/accept4_01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/access/Makefile

Purpose: LTP leaf Makefile for `access()` syscall tests. It includes the standard testcase and generic leaf makefiles with no custom compiler or linker settings. Runtime root, fork, tmpdir, read-only filesystem, and buffer needs are declared in individual C tests. State is build-only. Risk is low and limited to LTP make infrastructure. Test signal is successful compilation of `access01` through `access04`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/access/access01.c

Purpose: large permission matrix for `access(2)` with `F_OK`, `R_OK`, `W_OK`, `X_OK`, and combinations on files and files under directories with different modes. Setup creates root-owned files and directories with read/write/execute combinations, finds the nobody uid, and uses fork/setuid to test selected cases as nobody while root cases run in-process. Important data is the `tcases` table with expected errno and user mask; important APIs are `access`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_SETUID`, and `SAFE_FORK`. State is a tmpdir tree whose permissions are the core input. Dependencies are root and normal Unix permission semantics. Risks include filesystem permission mangling or root special-casing; test signal is exact pass or `EACCES` per matrix entry.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/access/access02.c

Purpose: positive `access()` behavior test for files and symlinks as both root and nobody. Setup creates files with no/read/write/execute permissions, makes the executable a shell script, and creates symlinks to each; each testcase calls `access` and then validates the permission by `stat`, `open`, or `system("./target")`. Important APIs are `access`, `stat`, `open`, `system`, `SAFE_SYMLINK`, `SAFE_SETUID`, and `SAFE_FORK`. State is a tmpdir containing real files and symlinks. Dependencies are root, a nobody account, `/bin/sh` path from `_PATH_BSHELL`, and executable tmpdir semantics. Risks are noexec mounts or symlink policy differences; test signal is both `access` success and corroborating operation success.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/access/access03.c

Purpose: verifies `access()` returns `EFAULT` for an invalid pathname address under each access mode and for both root and nobody. The testcase table passes `(void *)-1` with `F_OK`, `R_OK`, `W_OK`, and `X_OK`; `verify_access` runs the root check, forks, drops the child to nobody, and repeats. Important APIs are `access`, `SAFE_FORK`, `SAFE_SETUID`, and LTP expected-failure macros. State is process credentials only; no filesystem fixtures are created. Dependencies are root and a nobody account. Risks are architecture-specific bad-address handling, but the test encodes expected kernel ABI behavior. Test signal is `EFAULT` in all variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/access/access04.c

Purpose: negative `access()` errno coverage for invalid mode, empty/nonexistent path, too-long path, non-directory path component, symlink loop, and write access on read-only filesystem. Setup creates files, a file used as a path prefix, and a two-link symlink loop; LTP supplies a read-only mount at `mntpoint`. `verify_access` runs each case as root and as nobody. Important APIs are `access`, `SAFE_TOUCH`, `SAFE_SYMLINK`, fork/setuid helpers, and `.needs_rofs`. State includes tmpdir fixtures, a long pathname buffer, and a read-only mountpoint. Dependencies are root, nobody, and rofs support. Risks are errno differences for empty path or read-only mounts on unusual filesystems; test signal is exact expected errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/access/access04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/acct/Makefile

Purpose: LTP leaf Makefile for process accounting syscall tests. It includes standard testcase and leaf target makefiles without extra flags. Runtime kconfig, root, read-only filesystem, helper executable, and accounting file behavior are declared in the C files. State is build-only. Risks are minimal, though `acct02` depends on building `acct02_helper` alongside the test binary. Test signal is successful compilation of `acct01`, `acct02`, and helper.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct01.c

Purpose: verifies failure errno behavior of `acct()` across invalid accounting file inputs. Setup ensures accounting can be enabled then disabled on a tmp file, creates a symlink loop, prepares an overlong pathname, and uses LTP rofs mount support; selected cases temporarily drop euid to nobody or map a protected address for `EFAULT`. Important APIs are `acct`, `SAFE_CREAT`, `SAFE_SYMLINK`, `SAFE_MMAP`, `SAFE_SETEUID`, and `.needs_kconfigs`. State includes the accounting subsystem global switch, temporary files, rofs path, bad memory mapping, and euid changes. Dependencies are root and `CONFIG_BSD_PROCESS_ACCT=y`. Risks are global process accounting side effects and filesystem-dependent errno. Test signal is exact errno for EISDIR, EACCES, ENOENT, ENOTDIR, EPERM, ELOOP, ENAMETOOLONG, EROFS, and EFAULT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02.c

Purpose: validates that process accounting writes a correct `struct acct` or `struct acct_v3` entry for `acct02_helper`, and covers a free-space accounting regression. Setup checks filesystem free space, disables existing accounting, detects `CONFIG_BSD_PROCESS_ACCT_V3`, chooses record size, and gets clock ticks. `run` enables accounting to `acct_file`, records start time, runs the helper through `tst_cmd`, disables accounting, then scans records until the helper entry validates command name, uid/gid, start time, elapsed/sys/user time bounds, exit code, and v3 pid/ppid/version fields. Important APIs are `acct`, `SAFE_READ`, `tst_kconfig_read`, `tst_cmd`, and compact accounting field unpacking. State includes global accounting output and the generated accounting file. Dependencies are root-effective accounting permission and `CONFIG_BSD_PROCESS_ACCT`. Risks are other processes writing accounting records and low free-space silent discard behavior; test signal is finding a valid helper record.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02_helper.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02_helper.c

Purpose: tiny helper program used only by `acct02` to generate a predictable process accounting record. It sleeps for one second and exits with status 128. Important APIs are `sleep` and `return` from `main`; there is no LTP harness in this file. State is only process runtime and exit status. Dependencies are that the helper is built and executable in the test environment. Risks are minimal; if it is missing or renamed, `acct02` cannot find an accounting entry with command name `acct02_helper`. Test signal is indirect through `acct02` parsing its accounting record.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/acct/acct02_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/Makefile

Purpose: LTP leaf Makefile for Linux key retention service `add_key()` tests. It includes standard testcase make rules, appends `$(KEYUTILS_LIBS)` to `LDLIBS`, and delegates targets to `generic_leaf_target.mk`. Runtime requirements include root, key quotas, user management commands, and key type support declared per C file. State is build-only. Dependency risk is missing keyutils library settings causing link failure. Test signal is successful build of all `add_key0*.c` programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key01.c

Purpose: checks payload length limits for key types `keyring`, `user`, `logon`, and `big_key`. Setup probes whether `logon` and `big_key` are supported; each testcase calls `add_key` into `KEY_SPEC_THREAD_KEYRING` with a boundary payload length and expects success or `EINVAL`. Important APIs are `add_key`, keyring constants from `lapi/keyctl.h`, LTP allocated payload buffers, and root requirement for large payload limits. State is keys created in the thread keyring and large test buffers up to 1 MiB. Dependencies are kernel keyring support and available memory/quotas. Risks are unsupported key types and quota side effects; test signal is correct boundary acceptance/rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key02.c

Purpose: CVE-2017-15274 regression test ensuring `add_key()` with NULL payload and nonzero length fails with `EFAULT` rather than dereferencing NULL or returning the wrong error. It iterates key types including asymmetric, cifs, pkcs7, rxrpc, user, logon, and big_key, with type-specific payload lengths. Important APIs are `add_key`, `KEY_SPEC_PROCESS_KEYRING`, and LTP errno handling. State is no successful key insertion expected; process keyring may be touched only on unexpected success. Dependencies are optional key type modules; unsupported types are `TCONF` on `ENODEV`, and asymmetric without parsers may be `EBADMSG`. Risks are environment-specific support matrix; test signal is `EFAULT` for supported vulnerable key types.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key03.c

Purpose: regression test for preventing a user from precreating another user's `_uid.*` keyrings. It finds an unused uid by scanning passwd entries, creates process-keyring keyrings named `_uid.<uid>` and `_uid_ses.<uid>` as root, drops to that uid, then obtains the actual user and user-session keyring IDs and ensures they are not the fakes. Important APIs are `add_key`, `keyctl(KEYCTL_GET_KEYRING_ID)`, `SAFE_SETUID`, and passwd lookup. State includes fake keyrings in the process keyring and changed process credentials. Dependencies are root and keyring support. Risks are assumptions about unused uid discovery and keyring auto-creation semantics. Test signal is that fake keyrings do not become the target user's special keyrings.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key04.c

Purpose: CVE-2017-12193 regression test for associative-array node splitting in keyrings. It joins a new session keyring, forks a child, fills the keyring with 16 child keyrings to occupy the fan-out, then adds one `user` key; parent interprets normal child exit as pass and SIGKILL as likely kernel oops. Important APIs are `keyctl(KEYCTL_JOIN_SESSION_KEYRING)`, `add_key`, fork/wait macros, and generated descriptions. State is a session keyring populated with crafted entries. Dependencies are keyring support and fork. Risks are crash-oriented behavior on vulnerable kernels; test signal is child survival without verifier/kernel fatal signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key05.c

Purpose: verifies unprivileged key quota boundary behavior for maximum bytes and maximum keys, covering exact-quota regression commits. It creates up to ten temporary users, lowers key GC delay and quota sysctls via LTP save/restore, forks as each user, seeds a key, reads `/proc/key-users`, then attempts one over-quota and one exact-limit insertion. Important APIs are `useradd/userdel/groupdel` via `tst_cmd`, `add_key`, `/proc/key-users` scanning, `SAFE_SETUID`, and save_restore sysctl support. State includes temporary system users, user keyrings, key quota usage, and restored `/proc/sys/kernel/keys/*` settings. Dependencies are root, account-management commands, writable key sysctls, and keyring support. Risks include asynchronous key freeing and quota races; test signal is `EDQUOT` over limit and success exactly at max bytes/keys.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/add_key/add_key05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/Makefile

Purpose: LTP leaf Makefile for `adjtimex()` tests. It includes the standard testcase and generic leaf target makefiles without extra linker flags. Runtime root, syscall variant, and time-state restoration logic are in the C files. State is build-only. Risk is low because all special behavior is source-level. Test signal is successful compilation of the three adjtimex test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex01.c

Purpose: positive root test for `adjtimex()` setting clock adjustment fields. Setup saves current timex parameters; `verify_adjtimex` copies them, sets `SET_MODE` fields, expects a return status in `TIME_OK..TIME_ERROR`, then repeats with `ADJ_OFFSET_SINGLESHOT`. Important APIs are `adjtimex`, `struct timex`, and LTP buffer allocation. State is system clock discipline parameters, with saved values used as the base but no explicit cleanup restoration in this file. Dependencies are root/CAP_SYS_TIME. Risks are altering live system time discipline and environmental clock status. Test signal is successful syscall status range for both mode sets.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex02.c

Purpose: negative `adjtimex()` errno test across libc and direct syscall variants. It saves current parameters, computes HZ-scaled tick limits, then tests EPERM as nobody, EFAULT for direct syscall bad pointer, and EINVAL for `ADJ_TICK` below and above permitted range; cleanup restores saved parameters using `SET_MODE`. Important APIs are `adjtimex`, `tst_syscall(__NR_adjtimex)`, `SAFE_SETEUID`, `SAFE_SYSCONF`, and LTP variants. State includes system clock parameters and temporary euid changes. Dependencies are root and a nobody account. Risks are libc hiding EFAULT, explicitly skipped, and live clock side effects if cleanup fails. Test signal is exact expected errno per variant/case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex03.c

Purpose: CVE-2018-11508 regression test for a 4-byte kernel data leak via `adjtimex()` invalid mode handling. It loops ten times, zeroes a `struct timex`, sets invalid mode `0x8000`, expects `EINVAL`, then checks that `buf->tai` remains zero. Important APIs are `adjtimex`, `memset`, and LTP expected error reporting. State is only the userspace timex buffer; the invalid mode should not apply clock changes. Dependencies are standard `adjtimex` support. Risks are depending on `tai` as the leak sentinel and exact invalid-mode behavior. Test signal is all iterations returning `EINVAL` without nonzero `tai`, tagged to CVE and fix `0a0b98734479`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/adjtimex03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/Makefile

Purpose: LTP leaf Makefile for `alarm()` behavior tests. It includes standard testcase and generic leaf makefiles without custom flags. Runtime timing, signal handlers, fork behavior, and timeout metadata are contained in the C files. State is build-only. Risks are minimal. Test signal is successful build of the alarm test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm02.c

Purpose: verifies `alarm()` accepts large second values and returns the previous scheduled value when canceled. Setup installs a `SIGALRM` handler; each testcase schedules `INT_MAX`, `UINT_MAX/2`, or `UINT_MAX/4`, immediately calls `alarm(0)`, expects the same value, and checks no signal fired. Important APIs are `alarm`, `SAFE_SIGNAL`, and volatile signal counter state. State is per-process alarm timer. Dependencies are signal delivery semantics. Risks include platforms limiting alarm seconds differently. Test signal is returned remaining time equals requested large value and no premature `SIGALRM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm03.c

Purpose: confirms alarms are not inherited across `fork()`. The parent schedules `alarm(100)`, forks, child calls `alarm(0)` and should get zero, while parent cancels and expects 100 seconds remaining. Important APIs are `alarm`, `SAFE_FORK`, and LTP expected-value macros. State is parent and child process alarm timers. Dependencies are fork semantics. Risks are small timing windows but the operations are immediate. Test signal is child has no inherited alarm and parent retains its alarm.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm05.c

Purpose: checks alarm replacement return value and eventual signal delivery. It sets a 10-second alarm, sleeps one second, replaces it with a 1-second alarm expecting return value 9, sleeps two seconds, then expects exactly one `SIGALRM`. Important APIs are `alarm`, `sleep`, `SAFE_SIGNAL`, and signal counter state. State is the process alarm timer and volatile counter. Dependencies are scheduler timing accurate enough for the short sleeps; `.timeout=2` bounds LTP runtime. Risks are timing flake under heavy load. Test signal is remaining value 9 and one delivered signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm06.c

Purpose: verifies `alarm(0)` cancels a pending alarm. Setup installs a handler; run schedules two seconds, sleeps one, cancels and expects one second remaining, then sleeps past the original expiry and expects zero signals. Important APIs are `alarm`, `sleep`, and `SAFE_SIGNAL`. State is only the process alarm timer/counter. Dependencies are POSIX signal semantics. Risks are timing sensitivity but the sleeps have margin. Test signal is cancel return value 1 and no `SIGALRM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm07.c

Purpose: verifies a parent's scheduled `SIGALRM` is delivered to the parent, not a forked child. Setup installs a signal handler; run schedules one second, forks, both processes sleep three seconds, child expects counter zero, parent expects one. Important APIs are `alarm`, `SAFE_FORK`, signal handling, and LTP equality macros. State is per-process signal counter inherited as zero but updated independently. Dependencies are fork and signal semantics. Risks are timing under load; `.timeout=4` bounds the run. Test signal is parent count 1 and child count 0.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/Makefile

Purpose: LTP leaf Makefile for x86 `arch_prctl()` tests. It includes standard testcase and generic leaf makefiles without extra flags. Runtime architecture gating is declared in `arch_prctl01.c`. State is build-only. Risks are minimal. Test signal is successful compilation where syscall headers are available.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/arch_prctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/arch_prctl01.c

Purpose: tests `ARCH_SET_CPUID` and `ARCH_GET_CPUID` through `arch_prctl` on x86. Setup scans `/proc/cpuinfo` for `cpuid_fault`; each of two test indices tries to set CPUID faulting to the index, expecting success only when the CPU flag exists and `ENODEV` otherwise, then gets status and expects either the index or default 1. Important APIs are `tst_syscall(__NR_arch_prctl)`, `/proc/cpuinfo` parsing, `SAFE_FOPEN`, and string search. State is per-thread CPUID faulting control. Dependencies are x86/x86_64, kernel >= 4.12, and the CPU feature. Risks include incomplete cleanup/reset of the per-thread setting and fragile flag parsing. Test signal is set/get behavior matching feature availability.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/arch_prctl01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/Makefile

Purpose: LTP leaf Makefile for `bind()` tests. It includes standard testcase rules, adds `-pthread` to `bind04`, `bind05`, and `bind06`, and links `bind06` with `-lrt` for fuzzy sync/timing support. Runtime protocol, namespace, and filesystem requirements are declared in C files. State is build-only. Dependencies are pthreads and realtime library for selected tests. Risk is missing target-specific flags causing link failures. Test signal is successful build of all bind tests and shared header consumers.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind01.c

Purpose: errno and success coverage for `bind()` on invalid socket inputs and address conditions. Setup prepares IPv4 sockaddr values, a UNIX sockaddr pointing at `.`, a non-directory prefix case, opens `/dev/null`, and creates sockets; testcases expect EINVAL, ENOTSOCK, success for wildcard port, EAFNOSUPPORT, EADDRNOTAVAIL, EBADF, and ENOTDIR. Important APIs are `bind`, `socket`, `SAFE_OPEN`, `TST_GET_UNUSED_PORT`, and Unix/IPv4 sockaddr setup. State includes sockets, a tmpdir file used as a bad directory component, and bound port state. Dependencies are IPv4 and AF_UNIX. Risks include non-local address assumptions. Test signal is exact return/errno per case, with stream socket recreated after the successful bind.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind02.c

Purpose: verifies unprivileged binding to a privileged TCP port fails with `EACCES`. Setup looks up nobody and its group, switches effective gid/uid, and `run` attempts to bind an IPv4 stream socket to port 463 on `INADDR_ANY`. Important APIs are `SAFE_GETPWNAM`, `SAFE_GETGRGID`, `SAFE_SETEGID`, `SAFE_SETEUID`, `socket`, and `bind`. State is process credentials and one socket per run. Dependencies are root to drop privileges and classic privileged-port behavior. Risks include systems with `net.ipv4.ip_unprivileged_port_start` lowered enough to allow the port. Test signal is `bind()` failing with `EACCES`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind03.c

Purpose: regression check for AF_UNIX stream socket rebinding behavior and pathname cleanup after bind errors. Setup creates two Unix stream sockets, fills two pathname sockaddr structures, and binds the first to `socket.1`; run expects rebinding the same socket to `socket.2` to fail `EINVAL` and binding a second socket to `socket.1` to fail `EADDRINUSE`. It then checks kernel-version-dependent cleanup of `socket.2`. Important APIs are `bind`, `unlink`, `tst_kvercmp`, and safe Unix socket helpers. State is tmpdir socket pathnames and open sockets. Dependencies are AF_UNIX stream sockets. Risks include behavior differences before/after Linux 5.14 around leftover nodes. Test signal is expected errnos and absence/presence handling of `SNAME_B`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind04.c

Purpose: positive `bind()` and communication test for stream/seqpacket protocols over AF_UNIX pathname, AF_UNIX abstract, IPv4 loop/any TCP/SCTP, and IPv6 loop/any TCP/SCTP. Setup initializes sockaddr structures; each testcase binds a listening socket, resolves wildcard addresses with `tst_get_connect_address`, listens, starts a peer thread, accepts, exchanges a random testcase index and expected description string, then cleans socket files. Important APIs are `socket`, `bind`, `listen`, `accept`, `connect`, `SAFE_PTHREAD_CREATE`, and helpers from `libbind.h`. State includes sockets, temporary pathname socket files, and thread-local communication buffers. Dependencies are protocol availability, IPv6/SCTP support where configured, and pthreads. Risks are unsupported SCTP or network stack configuration. Test signal is successful round-trip string comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind05.c

Purpose: positive `bind()` and communication test for datagram protocols over AF_UNIX pathname/abstract, IPv4 UDP/UDP-Lite, and IPv6 UDP/UDP-Lite. Setup initializes loopback and wildcard socket addresses; each testcase binds a datagram socket, resolves wildcard connect address, starts a peer thread, receives an initial datagram, sends a random request index to the peer, reads the response string, and verifies it. Important APIs are `bind`, `connect`, `recvfrom`, `sendto`, `SAFE_READ`, pthread helpers, and shared constants from `libbind.h`. State includes bound datagram sockets, peer AF_UNIX socket path, and temporary socket files. Dependencies are protocol support and pthreads. Risks include UDP-Lite availability and AF_UNIX bidirectional binding requirements. Test signal is expected description string returned from the peer.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind06.c

Purpose: CVE-2018-18559 race test for AF_PACKET `bind()` versus network interface notifier state changes. Setup enters a network namespace, finds loopback ifindex, initializes two `sockaddr_ll` values, and configures a fuzzy-sync pair for 10000 loops. Run repeatedly creates an AF_PACKET datagram socket while thread B repeatedly binds it to addr1 and addr2; thread A toggles loopback interface flags around the race window and closes the socket. Important APIs are `SAFE_SOCKET(AF_PACKET)`, `ioctl(SIOCGIFINDEX/SIOCSIFFLAGS)`, `bind`, `tst_fzsync_pair`, and namespace setup. State includes netns interface flags, a volatile shared fd, and synchronization state. Dependencies are user/net namespaces and long runtime. Risks include intentional race and taint detection on vulnerable kernels. Test signal is surviving the minimum runtime with no warning/die taint.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/bind06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/libbind.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bind/libbind.h

Purpose: shared constants and testcase descriptor for bind communication tests. It defines pathname and abstract AF_UNIX socket names, peer socket path, IPv4 loopback literal, buffer size, and `struct test_case` containing socket type, protocol, sockaddr pointer, length, and description. Dependencies are socket, Unix, and IP networking headers. State is none; the header only supplies compile-time definitions consumed by `bind04.c` and `bind05.c`. Integration point is the common array element shape used by stream and datagram test lists. Risks are pathname collisions if tests do not clean up and embedded NUL handling for abstract socket path. Test signal is indirect through bind04/bind05 successful compilation and runtime communication.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bind/libbind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/Makefile

Purpose: LTP leaf Makefile for eBPF syscall tests. It includes standard testcase rules, filters `bpf_common` out as a standalone executable target, adds `_GNU_SOURCE`, and links every test target against `bpf_common.o`. Runtime capability drops, memlock changes, taint checks, and CVE metadata are declared in C files. State is build-only. Dependencies are LTP make infrastructure and the shared helper object. Risks are missing the helper object dependency or BPF lapi headers. Test signal is successful compilation/linking of map and program tests against `bpf_common`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.c

Purpose: shared eBPF helper implementation for map creation, program loading, and socket-triggered execution. Important functions are `rlimit_bump_memlock`, `bpf_map_create`, `bpf_map_array_create`, `bpf_map_array_get`, `bpf_init_prog_attr`, `bpf_load_prog`, and `bpf_run_prog`. Control flow wraps `bpf()` syscalls with retry/error normalization, handles EPERM as configuration/capability failure, copies instruction arrays into guarded buffers before verifier submission, and attaches programs to a Unix datagram socket via `SO_ATTACH_BPF`. State includes raised `RLIMIT_MEMLOCK`, allocated instruction buffers, BPF map/program fds returned to callers, and socket pairs used for execution. Dependencies are `lapi/bpf.h`, socket helpers, LTP safe resource wrappers, and CAP_SYS_ADMIN/CAP_BPF policy. Risks are memlock quota, verifier log interpretation, and privileged BPF restrictions. Test signal is helper-level `TPASS` on program load or fatal `TBROK/TCONF` with verifier log.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.h

Purpose: shared declaration and macro header for the BPF tests. It defines `BPF_MEMLOCK_ADD`, `BUFSIZE`, `BPF_MAP_ARRAY_STX` instruction macro, and prototypes for the common map/program helpers. Integration point is direct inclusion by every `bpf_map01`/`bpf_prog0*` source. State is compile-time only, except the macro expands into BPF bytecode that looks up an array element and stores a register value. Dependencies are LTP BPF and socket lapi headers. Risks are instruction macro correctness and register side effects in caller bytecode. Test signal is indirect through successful verifier acceptance/rejection and map value checks in consumers.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_map01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_map01.c

Purpose: sanity-checks BPF hash and array map create, lookup, update, and readback behavior. Setup raises memlock, initializes 4-byte and 8-byte keys, and fills a 1024-byte value pattern. Each testcase creates a map, verifies empty lookup behavior (`ENOENT` for hash, zero-filled preallocated value for array), updates one element with `BPF_ANY`, and confirms lookup returns the same buffer. Important APIs are `bpf(BPF_MAP_CREATE/LOOKUP_ELEM/UPDATE_ELEM)`, `bpf_map_create`, `ptr_to_u64`, and LTP buffers. State includes one map fd per testcase and allocated key/value/attr buffers. Dependencies are BPF map support and memlock/capability policy. Risks are deferred map freeing under low memlock and environment EPERM. Test signal is pass for create, expected empty lookup behavior, update, and exact value comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_map01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog01.c

Purpose: basic eBPF program load/run test. It creates an array map, builds socket-filter bytecode that looks up key 0 and writes value 1, loads the program, attaches it to a Unix datagram socket, sends a packet, then reads map[0]. Important APIs are BPF instruction macros, `bpf_init_prog_attr`, `bpf_load_prog`, `bpf_run_prog`, and `bpf_map_array_get`. State includes map fd, program fd, verifier log buffer, and message buffer. Dependencies are BPF socket filter support and memlock limit. Risks are verifier rejection due to policy or kernel support, and map fd substitution in bytecode. Test signal is map value exactly 1 after program execution.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog02.c

Purpose: regression test for 64-bit arithmetic verifier sanitation, especially unprivileged pointer-arithmetic checks fixed by `3612af783cf5`. It drops CAP_SYS_ADMIN, creates a two-entry array map, loads bytecode that computes `2^60 + 1` and `2^60 - 1`, stores both values, runs the program, and validates both map entries. Important APIs are BPF ALU/load/store macros, capability metadata, helper map functions, and socket-triggered run. State includes BPF map/program fds and allocated key/value/log buffers. Dependencies are BPF verifier behavior and capability handling. Risks are policy disabling unprivileged BPF, memlock, and verifier differences. Test signal is both 64-bit arithmetic results matching expected constants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog03.c

Purpose: CVE-2017-16995 regression test for incorrect sign extension in `check_alu_op()`. It deliberately constructs verifier-hostile bytecode that, on vulnerable kernels, can compute an out-of-bounds map pointer and corrupt map metadata; loading the program is considered failure. Important APIs are `bpf(BPF_PROG_LOAD)`, custom retry predicate accepting non-EPERM verifier outcomes, verifier log printing, map update, and optional execution if the verifier accepts bad code. State includes a BPF array map, malicious program fd if accepted, log buffer, and map value used for diagnostics. Dependencies are BPF verifier and dropped CAP_SYS_ADMIN. Risks are crash/corruption on vulnerable kernels, with taint behavior possible. Test signal is verifier rejection with a nonempty log; acceptance is `TFAIL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog04.c

Purpose: CVE-2018-18445 regression test for verifier handling of 32-bit right-shift arithmetic. It loads crafted bytecode that should be rejected; if accepted, the test reports failure and runs it to expose possible kernel damage. Important APIs are BPF ALU32/ALU64 macros, `bpf(BPF_PROG_LOAD)`, verifier logs, taint checking, and dropped CAP_SYS_ADMIN. State includes a one-entry array map, optional bad program fd, log buffer, and message buffer. Dependencies are BPF verifier and taint detection. Risks are intentional potentially harmful bytecode on vulnerable kernels. Test signal is verifier rejection; acceptance is failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog05.c

Purpose: verifies runtime/verifier behavior for 32-bit div/mod by zero after CVE-2021-3444-related fixes. It first ensures pointer arithmetic support for the intended test context, then loads a program that performs `w7 /= w6` and `w7 %= w6` where 32-bit source is zero from a 64-bit `1<<32`, stores source/destination registers, runs it, and checks current upstream semantics. Important APIs are `BPF_MAP_ARRAY_STX`, helper load/run functions, capability drops for CAP_SYS_ADMIN and CAP_BPF, and taint checking. State includes an eight-entry map, program fd, key/value/log buffers, and message. Dependencies are BPF behavior, memlock, and policy allowing the test. Risks include upstream semantic changes for undefined division by zero and harmful verifier bypasses. Test signal is expected source preservation and destination values 0/div and `UINT32_MAX`/mod.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog06.c

Purpose: CVE-2021-4204 regression test for ring buffer helper out-of-bounds access through unchecked record pointer arithmetic. It creates a BPF ringbuf map, builds bytecode that reserves a record and submits a pointer shifted far before the record, and expects verifier rejection. Important APIs are `BPF_MAP_TYPE_RINGBUF`, `BPF_FUNC_ringbuf_reserve`, `BPF_FUNC_ringbuf_submit`, BPF program loading, taint checking, and capability drops. State includes ringbuf map fd, optional accepted program fd, log buffer, and socket-trigger message. Dependencies are kernel >= 5.8 and BPF ringbuf support. Risks are immediate crash or later memory corruption if vulnerable verifier accepts the program. Test signal is failed verification; loading the OOB program is `TFAIL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog07.c

Purpose: CVE-2022-23222 regression test for insufficient restrictions on `*_OR_NULL` pointer types returned by `ringbuf_reserve`. It creates a ringbuf map, attempts to load bytecode that does arithmetic on the possibly-null ringbuf pointer and uses it for a stack write, and expects verifier rejection. Important APIs are BPF ringbuf helpers, BPF ALU/JMP/store macros, `bpf_map_create`, verifier log output, taint checking, and capability drops. State includes map fd, optional program fd, buffers, and socket-trigger message. Dependencies are kernel >= 5.8 and BPF ringbuf/verifier support. Risks are crash/corruption if accepted and run. Test signal is `TPASS` on failed verification; accepted program is failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/bpf/bpf_prog07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/brk/Makefile

Purpose: LTP leaf Makefile for `brk()` tests. It includes the standard testcase and generic leaf target makefiles without custom flags. Runtime libc-vs-syscall variants are in the C sources. State is build-only. Risks are minimal. Test signal is successful build of `brk01` and `brk02`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk01.c

Purpose: basic `brk()`/`sbrk()` functionality test across libc and raw syscall variants. It gets the current break, verifies libc `brk` availability when applicable, then cycles 33 times through increasing, unchanged, and decreasing break addresses by roughly two pages minus one, checking the returned/current break equals the requested address and writing to newly allocated heap on expansions. Important APIs are `sbrk`, `brk`, `tst_syscall(__NR_brk)`, and `getpagesize`. State is the process heap break, intentionally moved during the test. Dependencies are conventional brk implementation. Risks include writing at the break boundary and allocator interactions, though no malloc is used in the loop. Test signal is every requested break address taking effect.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk02.c

Purpose: regression-style test that shrinking `brk()` can munmap multiple VMAs after an intervening `mprotect`. It records the initial break, expands by one page and two pages, mprotects the new page read-only to split VMA state, expands again, then restores the original break. Important APIs are `brk`, `sbrk`, raw `__NR_brk`, `mprotect`, and page-size arithmetic. State is process heap VMA layout and protection attributes. Dependencies are libc/raw brk variants and mmap VMA behavior. Risks include address arithmetic on `void *` as a GNU extension and process heap side effects. Test signal is all expansions/protection/restoration succeed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/brk/brk02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/Makefile

Purpose: LTP leaf Makefile for architecture-specific `cacheflush()` tests. It includes standard testcase and generic leaf makefiles without extra flags. Runtime syscall availability is handled by conditional compilation in `cacheflush01.c`. State is build-only. Risks are architecture header availability. Test signal is either successful build of the test or compile-time `TCONF` path when the syscall is unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/cacheflush01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/cacheflush01.c

Purpose: simple syscall pass test for `cacheflush()` when `__NR_cacheflush` exists. Setup allocates one page; testcases call the raw syscall for `ICACHE`, `DCACHE`, and `BCACHE`, defining missing constants for m68k-style headers. Important APIs are `tst_syscall(__NR_cacheflush)`, `SAFE_MALLOC`, and architecture `asm/cachectl.h`. State is one allocated userspace page. Dependencies are architecture syscall support; otherwise the file declares `TST_TEST_TCONF`. Risks are architecture-specific cache flag semantics. Test signal is syscall success for each cache selector.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/cacheflush01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/Makefile

Purpose: LTP leaf Makefile for Linux `cachestat()` tests. It includes standard testcase rules, links `-lrt`, and delegates to the generic leaf target. Runtime filesystem mounts, hugetlbfs, and descriptor iteration are declared in C files. State is build-only. Dependencies are LTP lapi support for modern `cachestat` and realtime library. Risks are syscall/header availability on older systems. Test signal is successful build of the cachestat suite.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat.h

Purpose: shared helper header for cachestat tests. It includes `tst_test.h` and `lapi/mman.h`, then defines `print_cachestat` to log all five counters at `TDEBUG`: cache, dirty, writeback, evicted, and recently evicted. State is none beyond reading the supplied `struct cachestat`. Integration point is common diagnostics in `cachestat01` and `cachestat02`. Dependencies are LTP result logging and lapi definitions of `struct cachestat`. Risks are only compile compatibility with syscall wrapper types. Test signal is indirect through clearer debug output when counter assertions fail.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat01.c

Purpose: verifies `cachestat()` counts cached pages written to regular files, with and without `fsync`. Setup determines page size, caps the page-count exponent based on test device size, and fills a page buffer; each run creates a file on the mounted test filesystem, writes `1<<i` pages, optionally fsyncs, calls `cachestat`, checks cache plus evicted equals page count, and when synced checks dirty pages are zero. Important APIs are `cachestat`, `SAFE_WRITE`, `fsync`, mount-all-filesystems metadata, and `print_cachestat`. State includes mounted test filesystems, temporary file contents, page cache state, and dirty/writeback counters. Dependencies exclude fuse/tmpfs and require a test device. Risks are page-cache eviction/writeback timing and device-size limits. Test signal is counter equality across page counts and sync modes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat02.c

Purpose: verifies `cachestat()` counts cached pages in POSIX shared memory objects. Setup gets page size and allocates page data; run creates unique `/cachestat_<pid>.bin` shm objects for page counts `1..512`, truncates and writes them, calls `cachestat`, and checks cache plus evicted equals page count. Important APIs are `shm_open`, `SAFE_FTRUNCATE`, `SAFE_WRITE`, `cachestat`, and `shm_unlink`. State is shared-memory objects, their page-cache residency, and allocated counters/range buffers. Dependencies are POSIX shm and `-lrt` linkage. Risks are stale shm objects if interrupted and cache timing. Test signal is expected page count from cachestat for every tested size.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat03.c

Purpose: negative errno coverage for `cachestat()`. Setup opens a normal tmpdir file and a file on hugetlbfs; testcases exercise invalid fd `EBADF`, NULL range `EFAULT`, NULL data `EFAULT`, invalid flags `EINVAL`, and hugetlbfs fd `EOPNOTSUPP`. Important APIs are `cachestat`, `SAFE_OPEN`, hugetlbfs LTP metadata, and allocated range/data buffers. State includes two open fds and mounted hugetlbfs with one required hugepage. Dependencies are hugetlbfs availability and modern cachestat syscall support. Risks include unsupported hugetlbfs setup or errno variation for unsupported fd classes. Test signal is exact expected errno for every invalid input.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat04.c

Purpose: exercises `cachestat()` over LTP's generic file descriptor corpus and verifies unsupported descriptors fail with `EBADF` while supported non-file-like descriptors report zero counters. `run` iterates `TST_FD_FOREACH`, logs each descriptor description, calls `cachestat`, and checks all counters zero on success. Important APIs are `TST_FD_FOREACH`, `tst_fd_desc`, `cachestat`, and `lapi/mman.h`. State is the fd set created by LTP and a mounted device at `mnt`. Dependencies are descriptor helper support and mount_device. Risks are kernel support expansion changing which descriptors return EBADF vs zero. Test signal is EBADF or all-zero counters only.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/cachestat04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capget/Makefile

Purpose: LTP leaf Makefile for `capget()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime capability drops and syscall variants are declared in the C files. State is build-only. Risks are minimal and limited to capability header/syscall availability. Test signal is successful build of `capget01` and `capget02`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget01.c

Purpose: verifies `capget()` works for Linux capability ABI versions 1, 2, and 3 and observes a dropped capability. Setup stores current pid; test metadata drops `CAP_NET_RAW`; each testcase fills the header version/pid, calls raw `__NR_capget`, and asserts `CAP_NET_RAW` is absent from effective capabilities. Important APIs are `tst_syscall(__NR_capget)`, `struct __user_cap_header_struct`, `struct __user_cap_data_struct`, and LTP capability metadata. State is process capability sets and allocated header/data buffers. Dependencies are Linux capabilities. Risks include bit-width assumptions for version 1 and capability environment. Test signal is syscall success and effective set lacking `CAP_NET_RAW`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget02.c

Purpose: negative `capget()` error handling test. Setup obtains an unused pid and bad address; cases cover bad header pointer `EFAULT`, bad data pointer `EFAULT`, bad version `EINVAL`, negative pid `EINVAL`, and nonexistent pid `ESRCH`. Important APIs are raw `__NR_capget`, `tst_get_unused_pid`, `tst_get_bad_addr`, and capability structs. State is allocated header/data buffers and bad pointer values. Dependencies are Linux capability syscall semantics. Risks include kernel returning preferred capability version through the header, which the test verifies after failures. Test signal is exact errno plus preferred version reset to v3 on unsupported version.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capget/capget02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capset/Makefile

Purpose: LTP leaf Makefile for `capset()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime root, fork, and capability setup are in C files. State is build-only. Risks are minimal. Test signal is successful compilation of all capset tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset01.c

Purpose: positive `capset()` test for Linux capability ABI versions 1, 2, and 3. Setup records current pid; each testcase calls `capget` to fill current data for that version and then calls `capset` with the same data, expecting success. Important APIs are raw `__NR_capget`, raw `__NR_capset`, and capability structs. State is current process capability sets, which should be unchanged because the same data is written back. Dependencies are Linux capabilities. Risks are environment-specific capability restrictions. Test signal is successful capset for all supported ABI version constants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset02.c

Purpose: negative `capset()` errno test for bad pointers, bad version, and invalid capability set relationships. Setup establishes a limited capability set containing NET_RAW, CHOWN, and SETPCAP, drops CAP_KILL from the bounding set, and gets a bad address. Testcases expect EFAULT, EINVAL, or EPERM when effective is not subset of permitted, permitted exceeds old permitted, or inheritable exceeds old/bounding constraints. Important APIs are raw `capset`, `prctl(PR_CAPBSET_DROP)`, and capability structs. State is process capability and bounding sets. Dependencies are root and capability support. Risks are mutating capability state for the running test process and preferred-version side effect checks. Test signal is exact expected errno and version normalization.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset03.c

Purpose: verifies `capset()` fails with `EPERM` when new inheritable capabilities are not a subset of old inheritable and old permitted without CAP_SETPCAP. Setup sets effective/permitted/inheritable to only CAP_KILL; run adds CAP_NET_RAW to inheritable and expects failure. Important APIs are raw `__NR_capset` and capability structs. State is process capability sets changed during setup. Dependencies are root. Risks are capability environment or CAP_SETPCAP presence altering semantics. Test signal is `EPERM` for the expanded inheritable set.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset04.c

Purpose: verifies `capset()` cannot modify another process's capabilities. Setup fills current capability data with `capget`; run forks a child that pauses, sets header pid to child pid, expects raw `capset` to fail with `EPERM`, then terminates and waits for the child. Important APIs are `SAFE_FORK`, `pause`, `SAFE_KILL`, `SAFE_WAIT`, `capget`, and `capset`. State includes a live child process and current capability data. Dependencies are fork and Linux capabilities. Risks are cleanup if the assertion path exits early, mitigated by explicit kill/wait in normal flow. Test signal is `EPERM` for different-process capset.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/capset/capset04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chdir/Makefile

Purpose: LTP leaf Makefile for `chdir()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime mount, root, tmpdir, and buffer needs are declared in C sources. State is build-only. Risks are minimal. Test signal is successful build of the chdir test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir01.c

Purpose: checks `chdir()` return values and errno for root and nobody across files, directories, blocked directories, current/parent/root paths, missing paths, and symlink loops on mounted filesystems. Setup changes into the mounted test filesystem, creates fixtures, detects filesystems that ignore permission bits or symlink support, and records the nobody user. Each run resets cwd, tests as root, optionally tests as nobody, and validates return/errno. Important APIs are `chdir`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `SAFE_SETEUID`, and mount-all-filesystems metadata. State includes current working directory, mounted filesystem fixtures, and effective uid changes. Dependencies are root, mount device, and filesystem permission semantics. Risks are filesystem-specific permission/symlink behavior, handled with `TCONF` skips. Test signal is expected success or errno per path/user.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir02.c

Purpose: verifies that absolute paths consisting only of slashes and shorter than `PATH_MAX` are accepted by `chdir()`. It fills a buffer with 1 to `PATH_MAX-1` slash characters, calls `chdir` for each, counts failures, and reports a single pass if none fail. Important APIs are `chdir`, buffer allocation via `.bufs`, and `TST_EXP_PASS_SILENT`. State is current working directory repeatedly set to root-equivalent slash paths. Dependencies are standard pathname normalization. Risks are runtime cost from PATH_MAX iterations and any platform-specific slash handling. Test signal is no failures for lengths 1 through PATH_MAX-1.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir04.c

Purpose: negative `chdir()` errno test for overlong path, nonexistent directory, and bad userspace address. Setup substitutes `tst_get_bad_addr` for the EFAULT case; run calls `chdir` and expects ENAMETOOLONG, ENOENT, or EFAULT. Important APIs are `chdir`, `tst_get_bad_addr`, and LTP expected-failure macros. State is a tmpdir but no created fixture is required. Dependencies are pathname errno behavior. Risks are long string length being below some kernels' full path limit but intended as component/path too long. Test signal is exact errno for each case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chdir/chdir04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/Makefile

Purpose: LTP leaf Makefile for `chmod()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime root, rofs, filesystem, and tmpdir requirements are specified in C files. State is build-only. Risks are minimal. Test signal is successful build of all chmod tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod01.c

Purpose: positive `chmod()` test for regular file and directory modes. Setup creates either `testfile` or `testdir_1` depending on test variant; each case applies modes including 0, execute bits, all permissions, setuid, setgid, and sticky combinations, then stats the object and compares mode bits after masking file type. Important APIs are `chmod`, `SAFE_STAT`, `SAFE_TOUCH`, `SAFE_MKDIR`, and LTP variants. State is one tmpdir object per variant. Dependencies are standard Unix mode bits. Risks include filesystem support for special bits. Test signal is `chmod` success and exact mode match.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod03.c

Purpose: verifies non-root owner can set sticky bit and permissions on owned file and directory when group constraints are satisfied. Setup drops effective uid to nobody, creates a file and directory, and run applies mode `01777` to both then checks sticky/permission bits. Important APIs are `SAFE_GETPWNAM`, `SAFE_SETEUID`, `chmod`, and `SAFE_STAT`. State is tmpdir fixtures owned by nobody and process euid changed to nobody. Dependencies are root to drop credentials and normal ownership semantics. Risks are filesystem special-bit behavior. Test signal is mode includes all requested `01777` bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod05.c

Purpose: verifies non-root owner can change directory mode but cannot set setgid when its groups do not match the directory group. Setup creates a directory, gives it nobody uid and a free gid outside nobody's group, sets supplementary groups to nobody's gid, then drops to nobody. Run calls `chmod` with sticky+setgid+directory+RWX bits and expects the resulting mode to equal requested mode without `S_ISGID`. Important APIs are `tst_get_free_gid`, `SAFE_SETGROUPS`, `SAFE_CHOWN`, `SAFE_SETEGID`, `SAFE_SETEUID`, `chmod`, and `stat`. State includes credential/group changes and directory ownership. Dependencies are root and group database. Risks are filesystem mode-bit semantics. Test signal is chmod returns success but setgid bit is cleared.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod06.c

Purpose: negative `chmod()` errno coverage for EPERM, EACCES, EFAULT, ENAMETOOLONG, ENOENT, ENOTDIR, EROFS, and ELOOP. Setup creates files/directories, a protected directory, a non-directory path prefix, an overlong path, a bad mapped address, and a symlink loop; selected case changes euid to nobody and restores root. Important APIs are `chmod`, `SAFE_MMAP(PROT_NONE)`, `SAFE_SETEUID`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_SYMLINK`, and LTP rofs mount support. State is tmpdir fixtures, rofs mountpoint, and credential changes. Dependencies are root and read-only filesystem support. Risks include filesystem permission quirks and bad-address handling. Test signal is exact expected errno for each condition.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod07.c

Purpose: verifies root can set sticky bit permissions on a file it does not own while in the file's group. Setup creates `testfile`, changes owner to nobody and group to `users` or `daemon`, then sets process gid to that group. Run applies `01777`, stats, and checks the expected bits. Important APIs are `SAFE_GETPWNAM`, `SAFE_GETGRNAM_FALLBACK`, `SAFE_CHOWN`, `SAFE_SETGID`, `chmod`, and `stat`. State includes file ownership/group and process gid. Dependencies are root and group database. Risks are special-bit behavior on the backing filesystem. Test signal is mode includes requested sticky/permission bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod08.c

Purpose: verifies `chmod()` on a symlink pathname affects the target file in the traditional followed-symlink path. `run` creates a regular file and symlink, stats through the symlink, calls `chmod(symlink, 01777)`, stats again, and checks the target mode changed to include requested bits. Important APIs are `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_STAT`, `chmod`, and `SAFE_UNLINK`. State is one file and symlink in tmpdir. Dependencies are symlink support and followed-path chmod behavior. Risks are modern symlink mode protections only apply to nofollow/procfd case tested separately. Test signal is target mode changed as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod09.c

Purpose: regression test for blocking mode changes of symlinks via an `O_PATH|O_NOFOLLOW` procfd path, tagged to `5d1f903f75a8`. Setup creates a file and symlink; run opens the symlink itself with nofollow, builds `/proc/self/fd/<fd>`, expects `chmod` to fail `ENOTSUP`, then stats both target and symlink to ensure neither mode became zero. Important APIs are `SAFE_OPEN` with `O_PATH|O_NOFOLLOW`, `chmod`, `SAFE_STAT`, `SAFE_LSTAT`, and procfd paths. State includes a symlink fd, target file, and symlink metadata. Dependencies are kernel >= 6.6, procfs fd paths, and all-filesystems support. Risks are filesystem-specific ENOTSUP behavior. Test signal is failed chmod and unchanged target/symlink modes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chmod/chmod09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/Makefile

Purpose: LTP leaf Makefile for `chown()` tests. It includes standard testcase rules, `../utils/compat_16.mk` for 16-bit uid/gid compatibility wrappers, and generic leaf targets. Runtime root/tmpdir/rofs requirements are declared in C files. State is build-only. Dependency risk is the compatibility make include and generated `CHOWN` wrapper. Test signal is successful compilation of all chown tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown01.c

Purpose: basic positive `chown()` test on a tmp file. Setup validates current euid/egid with 16-bit compatibility checks and creates `chown01_testfile`; run calls `CHOWN` to set the file to the same uid/gid and expects success. Important APIs are `CHOWN` from `compat_tst_16.h`, `UID16_CHECK`, `GID16_CHECK`, and `SAFE_FILE_PRINTF`. State is one temporary file. Dependencies are tmpdir and chown syscall support. Risks are uid/gid compatibility on old ABI variants. Test signal is `chown` success.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown02.c

Purpose: verifies root `chown()` clears setuid/setgid on executable files but preserves setgid on non-group-executable files. Setup creates two files; each run chmods the selected mode, calls `CHOWN` to current uid/gid, stats, and checks owner/group plus expected mode. Important APIs are `SAFE_CHMOD`, `CHOWN`, `SAFE_STAT`, and compatibility uid/gid macros. State is tmpdir files with special permission bits. Dependencies are root and filesystem support for setuid/setgid semantics. Risks are filesystem-specific special-bit preservation. Test signal is correct ownership and mode transformation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown03.c

Purpose: verifies non-root owner can change a file's group to its effective group and that setuid/setgid bits are cleared. Setup drops to nobody and creates a file; run as root resets group and special mode, drops to nobody, checks starting owner/mode, calls `CHOWN(filename, -1, egid)`, then verifies group changed and setuid/setgid cleared. Important APIs are `SAFE_SETEUID`, `SAFE_SETEGID`, `SAFE_CHOWN`, `SAFE_CHMOD`, `CHOWN`, and `SAFE_STAT`. State is file ownership/mode and process credentials. Dependencies are root and nobody user. Risks are filesystem mode-bit behavior. Test signal is chown success, expected owner/group, and cleared special bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown04.c

Purpose: negative `chown()` errno coverage for EPERM, EACCES, EFAULT, ENAMETOOLONG, ENOENT, ENOTDIR, ELOOP, and EROFS. Setup creates a symlink loop, non-directory prefix, files, a protected directory path, substitutes a bad address, and drops to nobody. Each case calls `CHOWN` with current uid/gid and expects a specific errno. Important APIs are `CHOWN`, `SAFE_SYMLINK`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_SETEUID`, and rofs support. State includes tmpdir fixtures, a read-only mountpoint, bad address pointer, and euid nobody. Dependencies are root, nobody, rofs, and compat chown wrapper. Risks are filesystem permission/errno variations. Test signal is exact errno per condition.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown05.c

Purpose: verifies root can set owner and group to arbitrary numeric ids and can use `-1` to preserve previous uid or gid. Setup creates `testfile`; cases change owner/group, owner only, group only, and no change, then stats and compares expected carried-forward values. Important APIs are `CHOWN`, `SAFE_STAT`, and LTP table-driven execution. State is one tmpdir file whose uid/gid changes across testcase order. Dependencies are root and uid/gid compatibility wrapper. Risks are using arbitrary ids that may not exist but should still be accepted numerically. Test signal is successful chown and expected persisted uid/gid after each case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/Makefile

Purpose: LTP leaf Makefile for `chroot()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime root/tmpdir/fork requirements are in the C files. State is build-only. Risks are minimal. Test signal is successful build of all chroot tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot01.c

Purpose: verifies unprivileged `chroot()` fails with `EPERM`. Setup records the tmpdir path, looks up nobody, and drops effective uid to nobody; run calls `chroot(path)` expecting EPERM. Important APIs are `tst_tmpdir_path`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, and `chroot`. State is process credentials and tmpdir path. Dependencies are root to drop privileges and a nobody account. Risks are capability retention that could allow chroot unexpectedly. Test signal is `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot02.c

Purpose: basic positive `chroot()` functionality test. Setup creates a file in the tmpdir and records tmpdir path; run forks a child, calls `chroot(path)`, then stats the file as `/<name>` inside the new root. Important APIs are `SAFE_FORK`, `chroot`, `stat`, `SAFE_TOUCH`, and `tst_tmpdir_path`. State is child process root directory and a fixture file. Dependencies are root and fork. Risks include child not exiting explicitly after assertions, but LTP handles child process lifecycle. Test signal is successful chroot and file visibility at new root.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot03.c

Purpose: negative `chroot()` errno coverage for overlong path, file-not-directory, missing directory, bad address, and symlink loop. Setup creates a regular file, obtains bad address, fills a long pathname, and creates a two-link directory-style symlink loop. Each testcase expects ENAMETOOLONG, ENOTDIR, ENOENT, EFAULT, or ELOOP. Important APIs are `chroot`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `tst_get_bad_addr`, and LTP buffers. State is tmpdir fixtures and allocated long path. Dependencies are symlink support and pathname errno semantics. Risks are path length/loop resolution differences. Test signal is exact errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot04.c

Purpose: verifies unprivileged `chroot()` to a directory without search permission fails with `EACCES`. Setup creates `chroot04_tmpdir` with mode 0222, looks up nobody, and drops euid. Run calls `chroot` on that directory expecting EACCES. Important APIs are `SAFE_MKDIR`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, and `chroot`. State is a tmpdir directory with no execute/search bit and process credentials. Dependencies are root and permission semantics. Risks include filesystems ignoring directory mode. Test signal is `EACCES`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/Makefile

Purpose: LTP leaf Makefile for `clock_adjtime()` tests. It includes standard testcase rules, links `-lrt`, and delegates to generic leaf targets. Runtime syscall/time64 variants and wall-clock restoration are in C files. State is build-only. Dependencies are realtime library and LTP syscall/timex helpers. Risks are older platforms without syscall variants handled by conditional arrays. Test signal is successful compilation of the clock adjustment tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime.h

Purpose: shared compatibility header for `clock_adjtime` syscall tests across old kernel timex and time64 timex layouts. It defines fallback `__kernel_old_timex` and `__kernel_timex` structures, `enum tst_timex_type`, `struct tst_timex`, wrappers for `__NR_clock_adjtime` and `__NR_clock_adjtime64`, `timex_show`, and typed get/set helpers for selected adjustment fields. Integration points are `clock_adjtime01.c` and `clock_adjtime02.c`, which use the wrappers to run variant tables. State is compile-time type abstraction plus mutable `struct tst_timex` buffers owned by callers. Dependencies are LTP timer/safe clock/lapi syscall headers and kernel timex ABI definitions. Risks are layout drift with kernel headers and field-selection macro misuse. Test signal is indirect: variants can manipulate and log timex fields consistently.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime01.c

Purpose: positive root test for `clock_adjtime(CLOCK_REALTIME)` adjustment modes across old and time64 syscall ABIs. Setup saves current timex, rejects leap-change statuses, adjusts tick/offset limits for HZ and nano mode, and marks support; each testcase gets current timex, sets a mode and optional delta, applies it, reads back, and verifies changed fields where applicable. Cleanup restores saved clock fields and original micro/nano resolution; test metadata sets `.restore_wallclock`. Important APIs are `sys_clock_adjtime`, `sys_clock_adjtime64`, `tst_timex_get`, `timex_get/set_field_*`, and `SAFE_SYSCONF`. State is live system clock discipline parameters. Dependencies are root/CAP_SYS_TIME and syscall variant availability. Risks are wall-clock side effects if cleanup fails and environmental NTP/leap state. Test signal is successful set/get for ADJ modes and exact readback for delta fields.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime02.c

Purpose: negative `clock_adjtime()` errno coverage across old and time64 syscall ABIs. Setup saves current realtime timex, computes invalid clock ids via `tst_get_max_clocks`, scales tick bounds by HZ, and obtains a bad address. Testcases expect EINVAL for invalid clock ids, EFAULT for bad timex pointer, EINVAL for tick below/above bounds, and EPERM after dropping to nobody for privileged adjustment. Cleanup restores saved clock fields and resolution. Important APIs are syscall wrappers, `tst_get_max_clocks`, `SAFE_SETEUID`, `timex_set_field_*`, and LTP wallclock restore metadata. State is live system clock parameters and temporary euid changes. Dependencies are root, nobody user, and clock_adjtime syscall support. Risks are kernel normalization of out-of-range values and clock state side effects. Test signal is exact expected errno per case.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/clock_adjtime02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/Makefile

Purpose: LTP leaf Makefile for `clock_getres()` tests. It includes standard testcase rules, adds an include path to the sibling `../utils` directory, links with pthread and realtime libraries, and delegates to generic leaf targets. The include path and libraries support clock utility helpers and threaded/time tests in that directory. State is build-only. Dependencies are pthreads, librt, and LTP utility headers. Risks are missing utility include path or libraries causing compile/link failures. Test signal is successful build of the clock_getres leaf tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_getres/Makefile -->
