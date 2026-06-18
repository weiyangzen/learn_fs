<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh

Purpose: this is the shell regression test for the `bootconfig` tool. It creates temporary initrd/config/output files, applies and removes bootconfig payloads, and verifies parser behavior against sample good and bad files.

Important APIs/functions: `xpass()` expects a command to succeed and increments the test counter; `xfail()` expects a command to fail. `cleanup()` removes temporaries and exits with the accumulated failure count. The script calls `bootconfig`, `dd`, `wc`, `expr`, `grep`, `diff`, `awk`, and sample files under `samples/`.

Control flow: the test starts with basic command and delete-without-bootconfig checks, creates a 4096-byte initrd and simple config, applies it, checks show output and exact aligned size, repeats apply to ensure replacement rather than growth, deletes and checks truncation, then tests noisy invalid tail bytes. It then exercises maximum node count, maximum file size, same-key append and override, quotes, duplicate tree branches, trailing-space behavior, parse error line/column reporting, all expected failure samples, and all expected success samples with rendered-output diffs.

State and persistence: all files are temporary under the requested test directory or current directory and are removed by the trap. `NG` and `NO` track failed and total test cases. The script mutates temporary initrd content repeatedly and relies on sample files for expected parser behavior.

Dependencies and integration points: it assumes the compiled binary is `${TESTDIR}/bootconfig`, `ALIGN=4`, and sample file names under `samples/`. It exercises the `main.c` initrd footer contract and the bootconfig parser linked into the tool.

Risks: unquoted variables and command arguments can break if `TESTDIR` contains spaces. Some test names and comments contain typos but do not affect behavior. The maximum-size test relies on `base64 -w0`, which is GNU-specific. The expected sample loop uses relative `samples/...` paths, so it must be run from the bootconfig source directory or an equivalent working directory.

Test signals: this script is itself the main signal for `main.c` correctness. Additional CI hardening could run it under a temp directory path containing spaces, under fault-injection wrappers for short writes/truncation failures, and with sanitizers for the C binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/test-bootconfig.sh -->
