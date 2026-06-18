# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/vmtest.sh

Purpose: this shell script runs HID selftests inside a virtme-ng virtual machine. It can optionally build the kernel, HID-BPF programs, and HID selftest binaries from the current source tree before booting a VM, then run `hid_bpf`, `hidraw`, and/or the Python HID pytest suite.

Important APIs, functions, and variables: `SCRIPT_DIR` and `KERNEL_CHECKOUT` locate the selftest tree and kernel root. `HID_BPF_TEST`, `HIDRAW_TEST`, and `HID_BPF_PROGS` point to test binaries/programs. `TEST_NAMES` and `TEST_DESCS` define runnable tests. `usage()`, `die()`, `check_args()`, `check_deps()`, and `check_vng()` validate invocation and environment. `handle_build()` runs `vng --kconfig`, optional remote build args, kernel build, HID-BPF build, and selftest build. `vm_start()`, `vm_wait_for_ssh()`, `vm_mount_bpffs()`, and `vm_ssh()` manage the guest. `run_test()` wraps each test with dmesg error/oops checks. `log()` and helpers prefix setup/host/guest output and append to a temp log.

Control flow: option parsing accepts build, remote host/container, qemu path, shell mode, verbosity, and selected test names. The script checks dependencies and vng version, optionally builds, boots the VM, waits for SSH, mounts bpffs, and either opens an interactive root shell or emits KTAP-style output for each selected test. It runs the test function by name and converts pass/skip/fail counts into a final kselftest exit code.

State and persistence: temporary pid/log files are created under `/tmp`; `cleanup()` terminates QEMU using the pidfile and removes it. VM state exists for the script lifetime. Build mode mutates the kernel tree by generating `.config`, building BPF objects, and building selftests.

Dependencies and integration points: requires `virtme-ng` (`vng`), busybox, qemu, pkill, ssh, pytest, kselftest KTAP helpers, `hid_bpf`, `hidraw`, and a kernel tree. It uses virtme-ng SSH config in `${HOME}/.cache/virtme-ng`.

Risks: only vng versions 1.36 and 1.37 are tested; `eval test_"${name}" "$@"` depends on earlier validation; log redirection is verbosity-dependent; dmesg error count increases from unrelated guest activity can fail tests; build mode may be expensive and host/container args are shell-expanded through arrays except the podman prefix string.

Test signals: KTAP plan/output, per-test `ok`/`not ok`, dmesg oops/error detection, and a final `SUMMARY: PASS=... SKIP=... FAIL=...` plus log path.
