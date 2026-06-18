# subset-b-008328 Research

Grouped research for the requested eCryptfs test-suite files and EncFS Rust configuration/crypto files. Each section preserves its source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247/test.c

Purpose: C regression test for Launchpad bug 994247 around `/dev/ecryptfs` misc device close ordering. It intentionally opens the eCryptfs misc device in a parent, forks a child inheriting the fd, closes the fd in the parent first, then signals the child to close its inherited descriptor.

Important APIs and functions: `main`, global `miscdev`, `sigusr1_handler`, `open`, `sigaction`, `fork`, `pause`, `kill`, `waitpid`, `close`. Control flow installs a `SIGUSR1` handler, forks, leaves the child paused, closes the parent fd, then asks the child to close and returns the child close status. State is only the process-shared inherited file descriptor value; persistence is none except kernel misc-device reference counting.

Dependencies and integration: Requires `/dev/ecryptfs` and a loaded eCryptfs kernel interface, normally driven by the surrounding kernel test harness. Risk is that failure modes can be kernel BUGs or hangs, not just nonzero exits. Test signal is binary: successful orderly close returns `0`; open, signal, wait, abnormal child exit, or child close failure returns `1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-994247/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count.sh

Purpose: Shell wrapper for an eCryptfs misc-device regression reproducer linked to LKML 2012-01-11. It ensures kernel eCryptfs support is present, runs the compiled `miscdev-bad-count/test` probe, and propagates its status.

Important APIs and functions: sources `../lib/etl_funcs.sh`, calls `etl_load_ecryptfs`, installs `test_cleanup` trap, and executes `${test_script_dir}/miscdev-bad-count/test`. Control flow is minimal: initialize `rc=1`, load eCryptfs or exit, run the C test, store `$?`, and exit through the trap.

State and persistence: No mount or key state is created; only shell `rc` and trap state. Dependencies are bash, `modprobe`/`/proc/filesystems` behavior through `etl_load_ecryptfs`, `/dev/ecryptfs`, and the sibling C binary. Integration point is the kernel test harness `run_tests.sh`, which treats the script exit code as pass/fail. Main risk is environment sensitivity: if eCryptfs cannot load or the misc device is absent, this reports failure unrelated to the bad-count bug.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count/test.c

Purpose: C probe for malformed count handling on `/dev/ecryptfs`. It writes a six-byte buffer to the misc device while passing an intentionally huge count (`1073741824`) and expects the kernel write path to reject the request.

Important APIs and functions: `main`, `open("/dev/ecryptfs", O_WRONLY)`, `write`, `close`. Control flow opens the misc device, writes using a small static buffer but a very large byte count, closes the descriptor, and returns `0` only if `write` failed. A successful write is considered a regression and returns `2`; open failure returns `1`.

State and persistence: No userspace persistent state; the test stresses kernel copy/count validation. Dependencies are the eCryptfs misc device and the wrapper that loads the module. Integration is direct with `miscdev-bad-count.sh`. Risks include undefined-looking userspace arguments intentionally used to validate kernel bounds; sanitizers or hardened libc wrappers may flag the test pattern, but kernel behavior is the target signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mknod.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mknod.sh

Purpose: Kernel filesystem sanity test that verifies special-device node creation through an eCryptfs mount preserves device major/minor values. It creates a character device `c 1 7` inside a temporary encrypted test directory and checks `stat -c%t:%T`.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `mknod`, `stat`, cleanup via `etl_remove_test_dir`, `etl_umount`, `etl_lumount`, `etl_unlink_keys`. Control flow prepares keys, lower mount, eCryptfs mount, creates a test directory, performs `mknod`, validates `1:7`, removes the node, and exits through cleanup.

State and persistence: Creates keyring entries, lower/upper mounts, and one transient special file. Dependencies include root privileges or `CAP_MKNOD`, eCryptfs, mount helpers, and a lower filesystem allowing device nodes. Integration is under kernel tests. Risks are privilege and mount-option sensitivity; failures may reflect environment policy rather than eCryptfs metadata behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mknod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap.sh

Purpose: Shell harness that verifies block mappings reported through the eCryptfs upper file are a subset of the underlying lower encrypted file’s block mappings. It writes a 1 MiB file, locates the corresponding lower inode, and invokes the C `mmap-bmap/test` comparator.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `dd`, `etl_find_lower_path`, and remount sequence `etl_umount`/`etl_mount_i`. Control flow mounts, writes the test file, finds the lower path using inode lookup, runs the comparator with lower and upper paths, then remounts before exiting.

State and persistence: Creates mounted test state, a 1 MiB file, and keyring entries; cleanup removes mounts, keys, and the test directory. Dependencies include FIBMAP-capable filesystems, root privileges, and the sibling C test. Risk: filesystems that do not support `FIBMAP` may zero mappings in the C code, changing signal quality; block allocation behavior can vary by lower filesystem.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap/test.c

Purpose: C comparator for lower and upper block maps. It checks that every block number returned for the eCryptfs upper file also appears in the lower encrypted file and that the upper file does not report more blocks than the lower file.

Important APIs and functions: `get_blocks`, `check_blocks`, `main`, `open`, `ioctl(FIGETBSZ)`, `fstat`, `ioctl(FIBMAP)`, `malloc/free`. Control flow reads block size and file size, computes block counts, gathers block numbers for both files, then performs nested membership checks.

State and persistence: Allocates transient arrays of block numbers; no writes. Dependencies are Linux `linux/fs.h` ioctls and filesystems supporting or at least tolerating `FIBMAP`. Integration is via `mmap-bmap.sh`. Risks: `FIBMAP` failures are silently represented as block `0`, so unsupported filesystems can mask or distort failures. The test signal is `EXIT_SUCCESS` for subset relation, `EXIT_FAILURE` for open/stat/ioctl allocation failures or mismatched mappings.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-bmap/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close.sh

Purpose: Regression harness for applications that `open`, `mmap`, close the fd, dirty the shared mapping, then `munmap`. It verifies encrypted file data survives unmount/remount by comparing `md5sum` before and after.

Important APIs and functions: shared `etl_*` mount/key helpers, `${test_script_dir}/mmap-close/test`, `md5sum`, `etl_umount`, `etl_mount_i`. Control flow mounts eCryptfs, creates a temp path, lets the C test write via mmap-after-close, hashes the file, remounts, hashes again, and passes if hashes are identical.

State and persistence: Creates an encrypted file whose dirty mmap pages must flush correctly into lower storage. Dependencies include keyring setup, lower/upper mounts, and the sibling C probe. Integration is a kernel test named for Launchpad regressions 870326/1047261. Risks include cache/timing sensitivity; the explicit remount is the persistence boundary and makes stale page-cache-only success less likely.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close/test.c

Purpose: C reproducer for dirtying a shared mmap after closing the file descriptor. It creates/truncates a file to 32 KiB, maps it writable, closes the fd, fills the mapping with `0xFF`, and unmaps.

Important APIs and functions: `main`, `open(O_RDWR|O_TRUNC|O_CREAT)`, `ftruncate`, `mmap(MAP_SHARED)`, `close`, `memset`, `munmap`. Control flow validates one path argument, prepares the file, maps it, closes before dirtying, writes page-sized chunks, then relies on `munmap` to flush.

State and persistence: Mutates file contents through the VM mapping, with persistence validated by the shell wrapper. Dependencies are POSIX mmap semantics and eCryptfs writeback correctness. Risks include returning raw `errno` values, which are useful but not normalized; failure can represent open/truncate/map/unmap errors or the kernel regression. Test signal is zero when the dirty-close sequence completes without syscall errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir.sh

Purpose: Shell harness for the directory mmap negative test. It mounts an eCryptfs filesystem and invokes the sibling C probe against a temporary directory.

Important APIs and functions: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `${test_script_dir}/mmap-dir/test`, cleanup trap with unmount/key unlink. Control flow is standard for eCryptfs kernel tests: prepare keys and mounts, create test directory, run C test with that directory, propagate status.

State and persistence: Only transient mount/key/test-directory state. Dependencies include eCryptfs mountability and the C binary. Integration is with kernel bug LP 400443 coverage in the C file. Risks are mostly setup-related; because the target operation is a negative syscall check, environment failures are separated by the C test’s `TEST_ERROR` path where possible.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir/test.c

Purpose: C negative test for `mmap()` on an eCryptfs directory. It checks the fix for LP 400443: mmaping a directory should fail with `ENODEV` instead of returning an address that later SIGBUSes.

Important APIs and functions: `main`, `open` on `argv[1]/.`, `mmap(PROT_READ, MAP_PRIVATE)`, `munmap`, `errno` checks. Control flow opens the directory, attempts a 4096-byte mmap, closes fd, fails if mmap succeeds, and fails if the errno is not `ENODEV`.

State and persistence: No persistent writes; reads directory metadata only. Dependencies are Linux directory-file behavior and eCryptfs VFS mmap handlers. Integration is via `mmap-dir.sh`. Risks include kernel/filesystem errno differences; the test is intentionally strict about `ENODEV`, so a generic failure with a different errno is treated as a regression. Test statuses distinguish pass, failed expectation, and setup/usage error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir.sh

Purpose: Shell harness for verifying `read()` on an eCryptfs directory returns the expected POSIX-style error. It prepares a mounted encrypted test directory and executes `read-dir/test`.

Important APIs and functions: same eCryptfs helper flow as neighboring tests: `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, cleanup via trap. Control flow sets up the mount, runs the C test on the temp directory, captures its exit code, and exits.

State and persistence: Transient keys, lower/upper mounts, and a test directory only. Dependencies are bash, keyctl/mount tooling through `etl_funcs.sh`, and the sibling compiled probe. Integration covers Ubuntu bug 719691. Risks are setup and errno-policy sensitivity; the C probe separates usage/open errors from semantic failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir/test.c

Purpose: C negative test for `read()` on an eCryptfs directory. It verifies the regression fix for LP 719691: reading a directory should fail and set `errno` to `EISDIR`, not `EINVAL`.

Important APIs and functions: `main`, `open(argv[1]/.)`, `read`, `close`, `errno` validation. Control flow opens the directory read-only, reads into a 4096-byte buffer, fails if read succeeds, checks `errno == EISDIR`, then exits pass.

State and persistence: No writes or persistent state. Dependencies are VFS/eCryptfs directory read behavior. Integration is through `read-dir.sh`. Risks include strict errno expectations across kernels; a different failure mode still indicates compatibility risk for applications relying on standard directory semantics. Test signals are `0` pass, `1` semantic failure, `2` usage/setup error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/setattr-flush-dirty.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/setattr-flush-dirty.sh

Purpose: Shell-only regression test for dirty-page flushing during setattr, tied to kernel bug 33372. It verifies that preserving timestamps during copy remains stable after sync through an eCryptfs mount.

Important APIs and functions: `test_same_timestamp`, `stat -c '%y'`, `touch`, `sync`, `sleep`, `cp -p`, and normal `etl_*` setup/cleanup. Control flow creates `original`, syncs and waits, copies with preserved metadata to `copy`, compares timestamps, syncs again, compares timestamps again, removes both files, and exits.

State and persistence: Creates two transient files whose timestamps are the test state. Dependencies include eCryptfs setattr/writeback behavior, lower mount, and system timestamp precision. Integration is a kernel safe/destructive test depending on harness categorization. Risks include timestamp granularity or clock quirks; the one-second sleep reduces ambiguity, while the second comparison specifically targets dirty-page side effects after sync.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/setattr-flush-dirty.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file.sh

Purpose: Shell harness for a file truncation stress test over eCryptfs. It computes a conservative lower-filesystem capacity, caps it at 16,384 KiB, then asks the C test to exercise truncation and extension.

Important APIs and functions: `etl_lmax_filesize`, `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, and `${test_script_dir}/trunc-file/test`. Control flow prepares mount state, chooses block count, runs the C test on `test.img`, and cleans up through the trap.

State and persistence: Transient keyring, mounts, temp directory, and test image. Dependencies include enough disk space and correct lower filesystem reporting; `etl_lmax_filesize` adjusts for btrfs/xfs quirks. Integration is a kernel filesystem data-integrity test. Risks include long runtime or ENOSPC on small lower filesystems; the cap and helper slop logic bound the workload.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file/test.c

Purpose: C data-integrity test for repeated file shrink and re-expand operations. It writes deterministic pseudo-random data, repeatedly truncates to half sizes, validates retained data and file size, expands back to full size, and verifies the new tail is zero-filled.

Important APIs and functions: `write_buff`, `read_buff`, `test_write_random`, `test_read_random`, `test_read_rest`, `test_exercise`, `sighandler`, `main`, plus `open`, `write`, `read`, `lseek`, `ftruncate`, `fstat`, `close`, `unlink`. Control flow seeds `random()` with a fixed value for repeatable content, performs full write/read sanity, loops `trunc_size >>= 1`, and validates both content preservation and hole/zero semantics after each extension.

State and persistence: Mutates one test file and removes it at the end. Dependencies are filesystem truncation semantics and eCryptfs block translation. Integration is via `trunc-file.sh`. Risks include a missing explicit return in `test_write_random` on success, though callers only test `< 0`; also heavy IO scales with selected size. Test signal is strong because it checks data bytes, size metadata, zero-fill behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/xattr.sh -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/xattr.sh

Purpose: Shell harness for extended attribute behavior through eCryptfs. It creates a regular file in an encrypted mount and runs the sibling C test to set/list/get/remove `user.*` attributes.

Important APIs and functions: standard `etl_*` setup/cleanup, simple file creation with shell redirection, `${test_script_dir}/xattr/test`, remount sequence after the probe. Control flow mounts, writes initial file contents, runs the C xattr check, stores its result, attempts removal, remounts, and exits.

State and persistence: Creates a test file and transient xattrs; keys and mounts are cleaned. Dependencies include lower filesystem `user_xattr` support, which `etl_funcs.sh` enables for ext2/3/4 defaults. Integration is a kernel metadata test. Risk: the script removes `$test_file1` rather than `$test_file`, likely a typo, but trap cleanup removes the enclosing directory. Remount after xattr operations provides some persistence pressure.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/xattr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/xattr/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/kernel/xattr/test.c

Purpose: C xattr correctness test for eCryptfs. It sets three `user.test*` attributes, validates `listxattr` length and ordering, reads each value back, removes all attributes, and verifies the list is empty.

Important APIs and functions: `setxattr`, `listxattr`, `getxattr`, `removexattr`, static `names` and `values`, `main`. Control flow iterates over known names/values, accumulates expected nul-terminated name-list length, checks `listxattr(NULL,0)`, checks the returned buffer sequentially, validates values, removes each xattr, and confirms no remaining attributes.

State and persistence: Mutates file extended attributes only. Dependencies are Linux xattr APIs and deterministic order from eCryptfs/lower filesystem; order sensitivity is a notable assumption because POSIX does not strongly promise ordering. Integration is via `xattr.sh`. Risk: 1024-byte list buffer is fine for this fixed set; failures indicate xattr passthrough, list sizing, value, removal, or ordering issues.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/xattr/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/Makefile.am -->
## sources/security-integrity/ecryptfs-utils/tests/lib/Makefile.am

Purpose: Automake fragment for shared eCryptfs test-library artifacts. It distributes `etl_funcs.sh` and builds the helper program `etl-add-passphrase-key-to-keyring`.

Important APIs and functions: `dist_noinst_SCRIPTS`, `noinst_PROGRAMS`, `_SOURCES`, and `_LDADD`. Control flow is build-system declarative: compile `etl_add_passphrase_key_to_keyring.c` and link it with `$(top_builddir)/src/libecryptfs/libecryptfs.la`.

State and persistence: Produces a non-installed test helper binary in the build tree; no runtime state. Dependencies are automake/libtool and libecryptfs. Integration is central: shell tests call `tests/lib/etl-add-passphrase-key-to-keyring` through `etl_funcs.sh` to populate the kernel keyring. Risks include build ordering/linkage failures breaking most kernel tests, because mount helpers depend on generated key signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/etl_add_passphrase_key_to_keyring.c -->
## sources/security-integrity/ecryptfs-utils/tests/lib/etl_add_passphrase_key_to_keyring.c

Purpose: Small C bridge exposing libecryptfs `ecryptfs_add_passphrase_key_to_keyring()` to shell tests. It converts a hex salt, adds a passphrase-based key to the kernel keyring, and prints the authentication token signature.

Important APIs and functions: `main`, `from_hex`, `ecryptfs_add_passphrase_key_to_keyring`, `printf`. Control flow validates exactly two arguments, decodes salt into `ECRYPTFS_SALT_SIZE`, calls libecryptfs, treats return code `1` (already in keyring) as success, prints the hex signature on success, and returns the library code otherwise.

State and persistence: Persists key material in the user keyring until tests unlink it; stack buffers hold salt and signature. Dependencies are libecryptfs headers/library and kernel keyring support. Integration is used by `etl_add_fekek_passphrase` and `etl_add_fnek_passphrase`. Risks include passphrase/salt shell-argument exposure and reliance on libecryptfs return-code convention.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/etl_add_passphrase_key_to_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/etl_funcs.sh -->
## sources/security-integrity/ecryptfs-utils/tests/lib/etl_funcs.sh

Purpose: Shared bash library for eCryptfs tests. It centralizes key creation/unlinking, disk-image creation, lower-filesystem mounting, eCryptfs mounting, capacity estimation, temporary test-directory creation/removal, and mapping an upper inode to its lower path.

Important APIs and functions: `etl_add_fekek_passphrase`, `etl_add_fnek_passphrase`, `etl_add_keys`, `etl_unlink_key_sig`, `etl_unlink_fekek`, `etl_unlink_fnek`, `etl_unlink_keys`, `etl_create_disk`, `etl_remove_disk`, `etl_load_ecryptfs`, `etl_construct_lmount_opts`, `etl_lmount`, `etl_lumount`, `etl_lmax_filesize`, `etl_mount_i`, `etl_umount_i`, `etl_umount`, `etl_create_test_dir`, `etl_remove_test_dir`, `etl_find_lower_path`.

Control flow and state: Defaults define passphrases, salts, lower filesystem options, and eCryptfs mount options. Functions communicate through exported `ETL_*` variables such as `ETL_FEKEK_SIG`, `ETL_FNEK_SIG`, `ETL_DISK`, `ETL_LMOUNT_SRC/DST`, and `ETL_MOUNT_SRC/DST`. Persistent state includes temporary disk images, mounted lower/upper filesystems, and kernel keyring entries.

Dependencies and risks: Requires bash, keyctl, modprobe, mkfs, mount/umount, df, find, stat, and root privileges for many paths. A notable bug-risk is tests like `[ -n "ETL_FNEK_SIG" ]` and `[ -z "lmount" ]` using literals rather than variables, which can force filename-encryption mount options or skip validation unexpectedly. Integration is broad: most kernel scripts source this file, so regressions cascade across the suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/lib/etl_funcs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/new.sh -->
## sources/security-integrity/ecryptfs-utils/tests/new.sh

Purpose: Template script for creating a new eCryptfs test. It contains GPL header boilerplate, author placeholders, standard `test_script_dir` and `rc` setup, sources `etl_funcs.sh`, installs a cleanup trap, and leaves a `# TEST` placeholder.

Important APIs and functions: `test_cleanup`, trap on `0 1 2 3 15`, source of `../lib/etl_funcs.sh`. Control flow is intentionally skeletal: initialize failure status, source helpers, trap cleanup, execute future test body, set `rc=$?`, and exit.

State and persistence: None beyond shell variables unless a future test fills in operations. Dependencies are bash and the test library. Integration role is developer-facing consistency rather than runtime suite execution. Risks are that copied tests may inherit minimal cleanup that does not remove mounts/keys unless authors expand it; the placeholders must be replaced to avoid meaningless tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/new.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/run_tests.sh -->
## sources/security-integrity/ecryptfs-utils/tests/run_tests.sh

Purpose: Main eCryptfs test-suite harness. It selects kernel and/or userspace tests by category or explicit list, prepares lower/upper mount points and optional disk images/devices, runs test scripts, and prints pass/fail summary.

Important APIs and functions: `run_tests_cleanup`, `run_tests`, `run_kernel_tests_on_existing_device`, `run_kernel_tests_on_created_disk_image`, `usage`, `getopts`, sourcing `kernel/tests.rc` and `userspace/tests.rc`, plus `etl_create_disk`/`etl_remove_disk`. Control flow validates mutually exclusive `-b` disk-image vs `-d` device modes, validates mount paths, creates temp mountpoints if needed, exports `ETL_LMOUNT_DST`, `ETL_MOUNT_SRC`, and `ETL_MOUNT_DST`, builds test lists from categories, and runs scripts while counting failures.

State and persistence: May create temporary mount directories and disk images; cleanup removes only directories it created and any ETL disk. Dependencies include bash, root privileges for kernel tests, mountable lower filesystems, and test rc files. Risks include destructive device usage via `-d`, category variable expansion with `eval`, and counting/reporting based only on script exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/run_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/Makefile.am -->
## sources/security-integrity/ecryptfs-utils/tests/userspace/Makefile.am

Purpose: Automake fragment for userspace libecryptfs tests. It marks `verify-passphrase-sig.sh` as a distributed `make check` script and builds helper binaries for passphrase signature and wrap/unwrap tests.

Important APIs and functions: `AUTOMAKE_OPTIONS = subdir-objects`, `dist_check_SCRIPTS`, `check_PROGRAMS`, `dist_noinst_DATA`, `dist_noinst_SCRIPTS`, conditional `if ENABLE_TESTS`, `_SOURCES`, `_LDADD`, and `TESTS`. Control flow is declarative: under tests-enabled builds, compile `verify-passphrase-sig/test` and `wrap-unwrap/test`, both linked against libecryptfs.

State and persistence: Build artifacts only. Dependencies are automake, libtool, and libecryptfs. Integration: `make check` runs only `verify-passphrase-sig.sh`; `wrap-unwrap.sh` is distributed but not in `TESTS`, likely run manually or by the custom harness. Risks are coverage gaps if non-`TESTS` scripts are assumed to run in CI.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig.sh -->
## sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig.sh

Purpose: Regression script for libecryptfs `generate_passphrase_sig()`. It runs a compiled C helper against three fixed passphrase/salt pairs and expected signature/FEKEK outputs derived from ecryptfs-utils version 30.

Important APIs and functions: variables `pass`, `salt`, `expected_sig`, `expected_fekek`, calls `${test_script_dir}/verify-passphrase-sig/test`. Control flow executes the helper for each vector, exits immediately on the first failure, and returns the final helper status.

State and persistence: No filesystem/keyring state; all checks are deterministic in process memory. Dependencies are bash and the linked C helper/libecryptfs. Integration is `make check` through `userspace/Makefile.am` and optional `run_tests.sh -U`. Risk is intentional compatibility lock-in: any cryptographic derivation change, even deliberate, must update vectors and compatibility expectations.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig/test.c

Purpose: C helper that validates libecryptfs passphrase signature and FEKEK derivation against expected hex outputs. It is the executable backend for `verify-passphrase-sig.sh`.

Important APIs and functions: `usage`, `main`, `from_hex`, `generate_passphrase_sig`, `to_hex`, `strcmp`. Control flow validates five arguments and exact hex lengths, zeroes buffers, decodes salt, calls `generate_passphrase_sig`, converts FEKEK to hex, and returns `EINVAL` if either signature or key material differs.

State and persistence: Sensitive key buffers are stack-allocated and not explicitly wiped after use. Dependencies are libecryptfs constants/functions. Integration is with automake `check_PROGRAMS` and the shell vector runner. Risks include strict buffer-size assumptions based on libecryptfs constants; the test is deterministic and gives strong compatibility signal for KDF/signature behavior but not for keyring integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap.sh -->
## sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap.sh

Purpose: Userspace wrapper for libecryptfs passphrase wrapping/unwrapping regression tests. It creates a temporary test path and passes it to the C helper.

Important APIs and functions: sources `etl_funcs.sh`, uses `etl_create_test_dir`, runs `${test_script_dir}/wrap-unwrap/test`, cleanup calls `etl_remove_test_dir`. Control flow does not mount eCryptfs; it relies on the helper writing a wrapped passphrase file at the supplied path.

State and persistence: Creates a temporary directory under the default or environment-provided parent and a file path used by the C helper; cleanup removes the directory. Dependencies are bash, the helper binary, and libecryptfs. Integration is distributed as a non-installed script and can be run by the custom harness. Risk: `test_dir` is used in cleanup before explicit initialization, but empty values are harmless in `etl_remove_test_dir`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap/test.c -->
## sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap/test.c

Purpose: C regression test for libecryptfs passphrase wrapping APIs. It verifies a known passphrase round trip, then exhaustively checks passphrase lengths from 1 through `ECRYPTFS_MAX_PASSWORD_LENGTH`, and finally verifies overlength input fails.

Important APIs and functions: `main`, `from_hex`, `ecryptfs_wrap_passphrase`, `ecryptfs_unwrap_passphrase`, `strlen`, `memcmp`. Control flow decodes the default salt, wraps to the supplied path with wrapping password `testwrappw`, unwraps and compares length/content, repeats for increasing passphrase lengths, then attempts an overlong passphrase and expects an error.

State and persistence: Writes and overwrites a wrapped-passphrase file at the path supplied by the shell wrapper; sensitive passphrase buffers are stack-resident and not wiped. Dependencies are libecryptfs and writable temporary storage. Integration is userspace library regression coverage. Risks include char generation beyond alphabetic range for long lengths, which is fine as byte data but can affect diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/.cirrus.yml -->
## sources/security-integrity/encfs/.cirrus.yml

Purpose: Cirrus CI configuration for non-Linux EncFS coverage, currently active for FreeBSD and with a commented macOS task. It builds, tests, and runs live FUSE mount tests on FreeBSD while marking the task `allow_failures: true`.

Important APIs and functions: `freebsd_instance`, `install_script`, `script`, `allow_failures`. Control flow installs bash, Rust, FUSE, pkgconf, OpenSSL, symlinks bash, loads `fusefs`/`fuse`, then runs `cargo build --release`, `cargo test`, and ignored live mount tests with `ENCFS_LIVE_TESTS=1`.

State and persistence: CI VM package installation and kernel module loading only. Dependencies are FreeBSD 15 UFS image, ports packages, Rust toolchain, and FUSE availability. Integration complements GitHub Actions Linux CI. Risks include allowed failures hiding regressions on FreeBSD; the commented macOS task documents intended FUSE-T setup but provides no active signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/.cirrus.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/.config/nextest.toml -->
## sources/security-integrity/encfs/.config/nextest.toml

Purpose: Cargo nextest configuration. It defines slow-test handling for the default profile.

Important APIs and functions: `[profile.default]` and `slow-timeout = { period = "10s", terminate-after = 3 }`. Control flow is declarative: tests exceeding 10 seconds are marked slow and killed after three periods, i.e. about 30 seconds.

State and persistence: No runtime state beyond nextest behavior. Dependencies are `cargo nextest`, used by the Taskfile `test` task. Integration provides faster feedback and a timeout guard for unit/integration tests, while live mount tests are run separately with `cargo test`. Risk: legitimate slow cryptographic or filesystem tests may be terminated unless they are excluded or run outside nextest.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/.config/nextest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/.github/workflows/ci.yml -->
## sources/security-integrity/encfs/.github/workflows/ci.yml

Purpose: GitHub Actions workflow for Rust CI on pushes and pull requests to `master`. It performs lint, release build, release tests, and live FUSE mount tests.

Important APIs and functions: workflow triggers, `CARGO_TERM_COLOR`, `actions/checkout@v4`, apt installation of `fuse libfuse-dev pkg-config`, `modprobe fuse`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --release`, `cargo test --release`, and ignored live mount test command with `ENCFS_LIVE_TESTS=1`.

State and persistence: Ephemeral CI runner state and loaded kernel module. Dependencies are Ubuntu latest, FUSE device/module support, Rust default toolchain, and system libfuse headers. Integration is primary Linux validation. Risks: `modprobe fuse` is continue-on-error, so live tests may fail later depending on runner capabilities; clippy with `-D warnings` makes lint drift fail builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/Cargo.toml -->
## sources/security-integrity/encfs/Cargo.toml

Purpose: Rust workspace/package manifest for EncFS 2.0 beta. It defines binaries, dependencies, build script dependencies, dev dependencies, and i18n metadata.

Important APIs and types: workspace includes `"."` and excludes `fuzz`; package uses edition 2024; build dependencies `prost-build` and `protoc-bin-vendored`; runtime dependencies cover crypto (`aes`, `aes-gcm`, `aes-gcm-siv`, `argon2`, `pbkdf2`, `sha*`, `hmac`, `zeroize`), FUSE (`fuse_mt`, `libc`), config serialization (`quick-xml`, `prost`, `serde`, `base64`), CLI/i18n/logging (`clap`, `rust-i18n`, `env_logger`, `log`), and utility crates.

Control flow: declarative; build.rs compiles protobufs. State and persistence are Cargo lock/build artifacts. Integration defines `encfsctl` and `encfsr` binaries. Risks include edition/toolchain requirements, native FUSE/OpenSSL-related dependencies, and crypto dependency compatibility. Test signal comes from dev dependency `tar` plus CI/Taskfile commands rather than manifest scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/Taskfile.yml -->
## sources/security-integrity/encfs/Taskfile.yml

Purpose: Task runner definitions for common EncFS development workflows: build, release build, macOS cross-target build, unit/integration tests, live tests, formatting, clippy, coverage, fuzzing, and cleanup.

Important APIs and functions: Taskfile version 3, variables `CARGO`, `LIVE_TIMEOUT_SECS`, `MACOS_TARGET`, tasks `build`, `build-release`, `build-osx`, `test`, `test-live`, `fmt`, `fmt-check`, `clippy`, `coverage`, `fuzz`, `fuzz-build`, `clean`. Control flow is command execution; live tests set `ENCFS_LIVE_TESTS=1` and `ENCFS_LIVE_MOUNT_TIMEOUT_SECS`.

State and persistence: Cargo build outputs, coverage outputs, fuzz artifacts. Dependencies include go-task, cargo-nextest, cargo-tarpaulin, cargo-fuzz/nightly for optional tasks, and FUSE for live tests. Integration provides local parity with CI plus fuzz entry points. Risks are optional tool availability and live test privilege/kernel requirements.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/Taskfile.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/build.rs -->
## sources/security-integrity/encfs/build.rs

Purpose: Build script that compiles `proto/encfs_config.proto` into Rust code for the V7 config format using a vendored `protoc`.

Important APIs and functions: `main`, `protoc_bin_vendored::protoc_bin_path`, unsafe `std::env::set_var("PROTOC", ...)`, `prost_build::Config::new().compile_protos`. Control flow obtains the vendored compiler path, exposes it through `PROTOC`, compiles the proto from `proto` include root, and returns `Ok(())` or panics on compile failure.

State and persistence: Generates Rust protobuf bindings in Cargo `OUT_DIR`; no source-tree output. Dependencies are build dependencies in `Cargo.toml`. Integration is consumed by `src/config_proto.rs` using `include!(concat!(env!("OUT_DIR"), "/encfs.v7.rs"))`. Risk: build fails if vendored protoc cannot be located or proto compilation errors; the unsafe env mutation is acceptable in single-threaded build-script context.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/Cargo.toml -->
## sources/security-integrity/encfs/fuzz/Cargo.toml

Purpose: Cargo-fuzz manifest for EncFS fuzzing. It defines a separate fuzz package excluded from the main workspace and one libFuzzer target.

Important APIs and functions: package `encfs-fuzz`, `cargo-fuzz = true`, dependencies `libfuzzer-sys` with `arbitrary-derive`, `arbitrary`, path dependency on parent `encfs`, and `fuse_mt`. The `[[bin]]` target `fuzz_file_ops` points to `fuzz_targets/fuzz_file_ops.rs` and disables test/doc/bench.

State and persistence: Fuzz build outputs and corpus/crash artifacts under the fuzz project. Dependencies require nightly Rust per `rust-toolchain.toml` and cargo-fuzz. Integration is exposed by Taskfile `fuzz` and `fuzz-build`. Risks include API drift between `fuse_mt` versions in fuzz vs main package and fuzz-only dependency build failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/fuzz_targets/fuzz_file_ops.rs -->
## sources/security-integrity/encfs/fuzz/fuzz_targets/fuzz_file_ops.rs

Purpose: Differential libFuzzer target for EncFS file operations. It applies random sequences of writes, reads, shrink truncates, and expand truncates to both `EncFs` and a plain in-memory reference buffer, comparing decrypted on-disk content after mutations and read slices.

Important APIs and types: `Op`, `FuzzInput`, `TempDir`, constants `MAX_OPS`, `MAX_WRITE_SIZE`, `MAX_FILE_SIZE`, `BLOCK_SIZE`, `BLOCK_MAC_BYTES`, `HEADER_SIZE`, helpers `make_request`, `make_cipher`, `make_encfs`, `ref_write`, `ref_slice`, `read_encfs_full`, `verify_full`, and `fuzz_target!`. Control flow creates an EncFs rooted in a temp dir, creates one file via FUSE-layer API, discovers its encrypted physical path, decrypts file IV from the header, then interprets up to 32 operations with bounds to keep inputs manageable.

State and persistence: Uses a temporary encrypted directory removed on drop; in-memory reference tracks expected plaintext. Dependencies include EncFS config/crypto/fs APIs, `FileDecoder`, `SslCipher`, `fuse_mt::FilesystemMT`, and libFuzzer arbitrary generation. Integration specifically exercises block boundaries, MAC verification, sparse-hole handling, and truncate expansion with `allow_holes=true`. Risks: only one deterministic test config is covered, full-file decrypt after every operation is expensive, and it bypasses mounted kernel FUSE behavior by using the filesystem object directly.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/fuzz_targets/fuzz_file_ops.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/rust-toolchain.toml -->
## sources/security-integrity/encfs/fuzz/rust-toolchain.toml

Purpose: Rust toolchain pin for the fuzz subproject.

Important APIs and functions: `[toolchain] channel = "nightly"`. Control flow is rustup declarative selection when commands run inside `fuzz/`.

State and persistence: Causes rustup to install/select nightly if needed; no project runtime state. Dependencies are rustup and nightly compatibility with cargo-fuzz/libFuzzer. Integration matches Taskfile fuzz commands that explicitly use `cargo +nightly fuzz ...`. Risk: nightly drift can break fuzz builds; no date-pinned nightly is specified, so reproducibility is lower than the main package.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/fuzz/rust-toolchain.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/locales/ctl.yml -->
## sources/security-integrity/encfs/locales/ctl.yml

Purpose: i18n catalog for `encfsctl` administrative messages in English, French, and German. It covers config info display, password changes, Argon2 upgrade/calibration, cruft scanning, encoding/decoding, export, `cat`/`ls`, and new V7 config creation errors/prompts.

Important APIs and keys: `_version: 2` and many `ctl.*` keys such as `ctl.version7_config`, `ctl.v7_format_info`, `ctl.block_mode_aes_gcm_siv`, `ctl.kdf_algorithm_argon2id`, password prompts, file decode/export warnings, config-load/password errors, and `ctl.new_*`. Control flow is data-driven through `rust-i18n` `t!()` lookups from Rust CLI code.

State and persistence: No runtime state; persistent source of localized UI strings. Dependencies are YAML syntax and placeholder names matching call sites (`%{path}`, `%{error}`, etc.). Integration affects user-facing diagnostics and command help consistency. Risks include placeholder mismatches, untranslated semantic drift, and security-sensitive wording around invalid password/tampered config that must remain clear across locales.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/locales/ctl.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/locales/help.yml -->
## sources/security-integrity/encfs/locales/help.yml

Purpose: i18n catalog for clap help/about text for `encfs`, `encfsctl`, and `encfsr` command-line interfaces in English, French, and German.

Important APIs and keys: `_version: 2`, `help.encfs.*` for mount flags (`foreground`, `verbose`, `debug`, `public`, `extpass`, `stdinpass`, `read_only`, permissions, root/mount point), `help.encfsctl.*` for subcommands and options, and `help.encfsr.*` for reverse mode. Control flow is data-only; CLI builders or derive annotations call these keys through rust-i18n.

State and persistence: Static localized strings. Dependencies are correct YAML, stable key names, and placeholder-free help content. Integration shapes discoverability of security-sensitive options such as `--extpass`, `--stdinpass`, `--ignore-mac`, and reverse-mode unique-IV flags. Risks are stale help when CLI flags change; because help text is localized, every semantic option change requires catalog updates in all languages.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/locales/help.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/locales/lib.yml -->
## sources/security-integrity/encfs/locales/lib.yml

Purpose: Small library-level i18n catalog for errors emitted from non-CLI code paths.

Important APIs and keys: `_version: 2`, `lib.error_end_of_buffer`, `lib.error_version3_not_supported`, and `lib.error_unsupported_cipher` with `%{name}` and `%{key_size}` placeholders. Control flow is through `t!()` calls in modules such as `config_binary.rs` and `config.rs`.

State and persistence: Static localized error text only. Dependencies are `rust-i18n` and exact placeholder compatibility. Integration: these messages surface when parsing legacy binary configs, rejecting very old config versions, or constructing unsupported ciphers. Risks are limited catalog coverage: many library errors remain hardcoded English, so localization is partial and callers must handle mixed-language diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/locales/lib.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/locales/main.yml -->
## sources/security-integrity/encfs/locales/main.yml

Purpose: Runtime i18n catalog for the primary `encfs` binary and `encfsr` reverse-mode executable. It covers mount messages, config discovery, password prompting, daemonization, volume-key decryption, and reverse-mode validation errors.

Important APIs and keys: `main.mounting`, `main.using_legacy_config`, `main.no_config_file_found`, `main.failed_to_read_password`, `main.successfully_decrypted`, `main.daemonized_successfully`, `main.failed_to_decrypt_key`, `main.extpass_program_failed`, and `encfsr.*` validation messages. Control flow is data-driven via `rust-i18n` lookups from main/reverse binary code.

State and persistence: Static localization data. Dependencies are placeholder alignment with call sites (`%{root}`, `%{mount_point}`, `%{error}`, `%{source}`, `%{path}`). Integration is important for security UX because password and decrypt failure messages are user-facing. Risks include incomplete implementation notes (`encfsr.mount_not_implemented`) becoming stale if reverse mounting is implemented without updating locale text.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/locales/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/proto/encfs_config.proto -->
## sources/security-integrity/encfs/proto/encfs_config.proto

Purpose: Protocol buffer schema for EncFS V7 configuration. It models AEAD-wrapped volume keys, Argon2 KDF parameters, block cipher mode, filename encoding, feature flags, and a config hash used as authenticated associated data.

Important APIs and types: package `encfs.v7`; messages `Config`, `Argon2Kdf`, `BasicBlockCipher`, `AesGcmSivBlockCipher`, `NameEncoding`, `FeatureFlags`; enums `BlockCipherAlgorithm` and `NameEncodingMode`; `oneof cipher` with `legacy` and `gcm_siv`. Control flow is schema-driven: `build.rs` compiles it to Rust, `config.rs` converts between generated structs and `EncfsConfig`, and V7 save/load hashes the proto with `encrypted_key` and `config_hash` cleared.

State and persistence: Defines the on-disk `.encfs7` wire contract after the `ENCFS7\0` magic. Dependencies are prost/protoc. Risks are compatibility-sensitive field numbers; changing numbers or semantics would break existing configs. The explicit `config_hash` plus AEAD AAD improves tamper detection.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/proto/encfs_config.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/config.rs -->
## sources/security-integrity/encfs/src/config.rs

Purpose: Central EncFS configuration module. It loads legacy V4/V5 binary configs, V6 XML configs, and V7 protobuf configs; validates cryptographic and filesystem parameters; derives configured ciphers from passwords; and saves V6/V7 configs.

Important APIs and types: `ConfigType`, `KdfAlgorithm`, `BoostSerialization`, `EncfsConfig`, `Interface`, `EncfsConfig::standard_v7`, `load`, `validate`, `load_v4`, `load_v5`, `decode_v7_proto`, `load_v7_proto`, `load_v7`, `get_cipher`, `header_size`, `file_codec_params`, `block_mode`, `block_overhead_bytes`, `test_default`, `save`, `save_xml`, `set_v7_key`, `save_v7`, `encfs_config_to_proto_v7`, `v7_config_hash_from_proto`, XML serialization helpers, and `SslCipher::iv_len`.

Control flow: `load` reads bytes, detects V7 magic/name, rejects V3, tries V6 XML, falls back to V4 by name or V5 binary. Validation rejects unsupported `plainData`, invalid sizes, unsupported block MAC random bytes, invalid V7 AES-GCM-SIV combinations, and incomplete Argon2 params. `get_cipher` validates, constructs `SslCipher`, derives user keys with PBKDF2/legacy/Argon2id, decrypts wrapped volume key, zeroizes derived blobs, and configures name encoding. V7 additionally authenticates `key_data` with AES-GCM using `config_hash` as AAD.

State and persistence: Persistent config files include `.encfs4`, `.encfs5`, `.encfs6.xml`, and `.encfs7`; in-memory config stores salts, encrypted key data, KDF params, block mode flags, and optional V7 hash. Dependencies include quick-xml, serde, base64, prost, sha2, zeroize, rust-i18n, config_binary, config_proto, crypto/aead, crypto/block, and crypto/ssl. Risks: compatibility across legacy formats is complex; V7 block mode is inferred partly by `block_mac_bytes == 16`, so sentinel semantics must stay stable. Tests cover fixture load/save, V7 round trips, hash mismatch, KDF and validation paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/config_binary.rs -->
## sources/security-integrity/encfs/src/config_binary.rs

Purpose: Parser for legacy EncFS binary configuration variables used by V4/V5 configs. It provides a byte-buffer cursor abstraction and a top-level key/value reader.

Important APIs and types: `ConfigVar`, `ConfigVar::new`, `at`, `read_int`, `read_int_default`, `read_bool`, `read_bytes`, `read_string`, `read_u8_vector`, `ConfigReader`, `ConfigReader::new`, `ConfigReader::get`. Control flow decodes variable-length integers with high-bit continuation, then length-prefixed byte/string values; `ConfigReader` reads an entry count and then repeated key/value blobs into a `HashMap`.

State and persistence: In-memory buffers and cursor offsets; persistent source is legacy `.encfs4/.encfs5` bytes. Dependencies are anyhow, rust-i18n for end-of-buffer error, and standard collections. Integration is used by `config.rs` `load_v4`/`load_v5` and `Interface::from_config_var`. Risks include accepting malformed VLQ sequences that end at buffer boundary without explicit continuation error, and UTF-8 validation that may be stricter than historical C++ behavior. Unit tests cover VLQ, string, and reader basics.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/config_binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/config_proto.rs -->
## sources/security-integrity/encfs/src/config_proto.rs

Purpose: Thin generated-code bridge for EncFS V7 protobuf bindings. It includes the Rust module generated from `proto/encfs_config.proto` by `build.rs`.

Important APIs and functions: `include!(concat!(env!("OUT_DIR"), "/encfs.v7.rs"))`. Control flow is compile-time inclusion: Cargo runs the build script, prost writes generated code to `OUT_DIR`, and this module exposes generated messages/enums under `crate::config_proto`.

State and persistence: No runtime state; depends on generated build output. Dependencies are `build.rs`, `prost-build`, vendored protoc, and the proto schema. Integration is used heavily by `config.rs` for V7 load/save/hash conversion. Risk: IDEs or tools that do not run build scripts may not resolve generated symbols; build failures in proto generation break this module.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/config_proto.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/constants.rs -->
## sources/security-integrity/encfs/src/constants.rs

Purpose: Shared constants for EncFS configuration defaults and buffer sizing.

Important APIs and values: `DEFAULT_SALT_SIZE` 20 bytes, `DEFAULT_KDF_ITERATIONS` 100000, Argon2 defaults `DEFAULT_ARGON2_MEMORY_COST` 64 MiB, `DEFAULT_ARGON2_TIME_COST` 3, `DEFAULT_ARGON2_PARALLELISM` 4, `DEFAULT_CONFIG_VERSION` 20260101, `DEFAULT_BLOCK_SIZE` 4096, `FILE_BUFFER_SIZE` 128 KiB, `V5_MIN_SUBVERSION` 20040813, and `XML_BASE64_LINE_LEN` 76.

Control flow: none; constants are consumed by config creation/validation, file operations, and legacy compatibility logic. State and persistence: values shape newly generated config files and runtime buffers, so changes are persistent for new volumes. Dependencies are none. Integration is visible in `EncfsConfig::standard_v7`, `test_default`, V5 version checks, and file IO paths. Risks: changing defaults affects compatibility, security cost, and performance; Argon2 defaults in particular alter unlock latency and memory pressure.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/aead.rs -->
## sources/security-integrity/encfs/src/crypto/aead.rs

Purpose: AES-256-GCM helper for wrapping and unwrapping V7 volume-key blobs using a config hash as associated authenticated data.

Important APIs and values: `GCM_NONCE_LEN`, `GCM_TAG_LEN`, `AEAD_KEY_LEN`, `encrypt`, `decrypt`. Control flow validates 32-byte key length, generates a random 96-bit nonce for encryption, encrypts in place with AAD, and returns `nonce || ciphertext || tag`; decryption splits that format and verifies the detached tag before returning plaintext.

State and persistence: Persistent output is the V7 `encrypted_key` blob in config files; nonce randomness comes from `getrandom`. Dependencies are `aes-gcm`, `anyhow`, and OS randomness. Integration is called by `EncfsConfig::set_v7_key` and `get_cipher`. Risks: key length and AAD must match exactly or configs become undecryptable; nonce uniqueness depends on OS RNG. Tests cover roundtrip, wrong key, wrong AAD, layout, and tampering of ciphertext/tag/nonce.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/aead.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/block.rs -->
## sources/security-integrity/encfs/src/crypto/block.rs

Purpose: Block-layout and per-block encryption/decryption abstraction for EncFS file data. It supports legacy EncFS block format with optional MAC prefix and V7 AES-GCM-SIV authenticated block mode.

Important APIs and types: constants `AES_GCM_SIV_BLOCK_TAG_BYTES` and `LEGACY_MAX_BLOCK_MAC_BYTES`, enum `BlockMode`, `BlockMode::from_config`, `overhead_bytes`, struct `BlockLayout` with size conversion helpers, and `BlockCodec` with `decrypt_block`/`encrypt_block` plus legacy and AES-GCM-SIV internals.

Control flow: `BlockLayout` validates block size exceeds overhead and maps physical/logical sizes. `BlockCodec::decrypt_block` treats all-zero sparse blocks as zeros when `allow_holes`, then dispatches by mode. Legacy decrypt calls `SslCipher::legacy_decrypt_block_inplace`, verifies a computed 64-bit MAC prefix unless ignored, and returns plaintext. AES-GCM-SIV decrypt splits tag/ciphertext and verifies via cipher. Encrypt performs the inverse, prepending MAC/tag and encrypting payload.

State and persistence: Defines on-disk block shape and authentication bytes. Dependencies include `SslCipher` methods and `ConfigType`. Integration is consumed by `crypto/file.rs` and config validation. Risks include sentinel selection of AES-GCM-SIV by V7 plus 16-byte MAC, strict MAC failures on corrupted legacy data, and sparse-hole zero-block special casing. Unit-level test coverage is largely through file codec tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/file.rs -->
## sources/security-integrity/encfs/src/crypto/file.rs

Purpose: File-level encoder/decoder for encrypted EncFS file contents. It maps logical plaintext offsets to physical encrypted blocks, handles per-file headers, legacy MAC/AES-GCM-SIV block overhead, read-modify-write partial blocks, sparse-hole behavior, and logical/physical size conversion.

Important APIs and types: traits `ReadAt`, `WriteAt`, `FileLen`; `FileCodecParams`; `FileDecoder::new`, `new_with_mode`, `new_from_config`, `calculate_logical_size`, `calculate_logical_size_with_mode`, `read_at`; `FileEncoder::new`, `new_with_mode`, `new_from_config`, `calculate_physical_size`, `calculate_physical_size_with_mode`, `write_at`, and internal `write_at_internal`.

Control flow: Decoding builds `BlockLayout`/`BlockCodec`, then loops over logical blocks, reads physical blocks at `header_size + block_num * block_size`, decrypts, slices requested bytes, and stops on EOF. Encoding calculates current logical size from physical length; if writing past EOF it fills the gap with encrypted zero blocks, then splits user data across logical block boundaries. Partial writes read and decrypt existing blocks for read-modify-write unless a write overwrites the existing payload from block start; encrypted blocks are written with `write_at`.

State and persistence: Mutates encrypted file bytes and relies on file headers and block metadata chosen by config. Dependencies are `crypto/block`, `SslCipher`, Unix `FileExt`, and callers such as FUSE filesystem and fuzz target. Risks include complexity around partial blocks, holes, offset arithmetic, and authentication failures during RMW. Tests use a mock file to cover size conversion, no-MAC round trips, MAC modes, partial writes, and AES-GCM-SIV layout.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/mod.rs -->
## sources/security-integrity/encfs/src/crypto/mod.rs

Purpose: Module declaration hub for EncFS crypto code.

Important APIs and modules: exposes `aead`, `block`, `file`, and `ssl` submodules. Control flow is compile-time module inclusion only; it defines the namespace used by the rest of the crate.

State and persistence: None directly. Dependencies are the corresponding Rust source files. Integration: callers import `crate::crypto::aead` for V7 key wrap, `block` for block modes/layout, `file` for file encode/decode, and `ssl` for cipher primitives/KDFs. Risks are low, but adding/removing modules here changes public internal paths across the crate and can break config, filesystem, and fuzz code.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/crypto/mod.rs -->
