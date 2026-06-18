# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.sh

`ir_loopback.sh` is the kselftest wrapper for the IR loopback helper. It checks root privileges, verifies the `rc-loopback` module is available, loads it, discovers the rc device, and runs `./ir_loopback` with that device as both sender and receiver.

Important commands are `/sbin/modprobe -q -n rc-loopback`, `/sbin/modprobe rc-loopback`, `grep` over `/sys/class/rc/rc*/uevent`, and the kselftest skip exit code `4`.

Control flow is linear: skip when not root, skip when the module cannot be found, load the module, derive `RCDEV` from sysfs, invoke the compiled helper, and exit with its status. State changes include loading `rc-loopback` and creating sysfs/dev nodes.

Dependencies are root, modprobe, the module, sysfs rc class entries, and a locally built `ir_loopback` binary. A risk is multiple matching rc-loopback devices expanding into multiple names. The script also does not unload the module. Test signals come from wrapper skips or helper pass/fail output.
