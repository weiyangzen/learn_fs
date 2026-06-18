# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2.sh

## Research

This shell selftest exercises BPF integration with LIRC mode2 devices through the kernel `rc-loopback` driver. It is an environment-dependent harness that skips when required privileges or loopback devices are absent.

The script requires root, loads `rc-loopback`, scans `/sys/class/rc/rc*/uevent` for `DRV_NAME=rc-loopback`, derives both the `/dev/lircN` and `/dev/input/eventM` paths from uevents, then runs `./test_lirc_mode2_user $LIRCDEV $INPUTDEV`. It prints colored PASS/FAIL output and exits with the helper status or kselftest skip code `4` if no loopback LIRC device is found.

State side effects are the loaded `rc-loopback` module, discovered LIRC/input device use, and kernel BPF subsystem state as driven by the C helper. The shell script itself does not persist files. Dependencies include root privileges, `modprobe`, `rc-loopback`, sysfs RC class entries, the compiled `test_lirc_mode2_user` binary, and kernel support for attaching BPF programs to LIRC mode2 hooks.

Risks are primarily environmental: missing root privileges, unavailable `rc-loopback`, missing device nodes, or incompatible kernel configuration will skip or fail. Test signals are skip messages, PASS/FAIL lines for `lirc_mode2`, and the helper's success/failure status for actual BPF LIRC behavior.
