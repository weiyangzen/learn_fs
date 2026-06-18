# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-qemu.sh

Purpose: executes and monitors one prepared qemu command for a rcutorture scenario, enforcing duration, shutdown grace, stop requests, and hang killing.

Important APIs and functions: reads settings embedded as comments in `qemu-cmd`, rewrites qemu command with optional `taskset`, redirects output, records `qemu-pid`, monitors `console.log`, writes `qemu-retval`, and removes `build.run` when done.

Control flow: validate scenario dir and qemu-cmd, decorate command, start qemu in background, discover pid, optionally wait for gdb attach, monitor until qemu exits, duration expires, or STOP.1 appears. If still running, grant shutdown grace while console output advances, then kill on hang or stop request.

State and persistence: writes `console.log`, `qemu-pid`, `qemu-retval`, `qemu-affinity`, and `Warnings`; removes run sentinel.

Dependencies and integration: called by direct and batch run scripts.

Risks and test signals: tail-based progress heuristics can misclassify quiet shutdowns. Unknown pid prevents killing. Warnings file captures early completion, external termination, and hangs.
