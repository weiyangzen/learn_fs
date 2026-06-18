# sources/distributed-fs/ceph-client/tools/usb/hcd-tests.sh

Purpose: this shell script is a long-running stress harness around `./testusb` for host-controller-driver and usbtest firmware coverage. It groups usbtest ioctl cases into named workloads such as `control`, `out`, `in`, `iso-out`, `iso-in`, `halt`, `unlink`, and `loop`.

Important APIs and commands: `do_test()` invokes `./testusb` with the selected device mode, buffer size, iteration count, and usbtest case arguments. `check_config()` enforces that mutually incompatible workload families are not mixed after a configuration assumption is established. `DEVICE` controls whether testing targets one device or all recognized devices via `-a`.

Control flow: defaults are `TYPES='control out in'`, `COUNT=50000`, and `BUFLEN=2048`, but the main infinite loop resets count and length for each type, dispatches a `case`, and exits on the first failing `testusb` command. Each branch tunes iterations, transfer size, scatter/gather length, and variation to exercise normal, short, unaligned, isochronous, halt, and unlink paths.

State and dependencies: persistent state is minimal; the script loops forever and prints timestamps and progress to stdout. It depends on Bash-style `declare -i` despite `#!/bin/sh`, on a locally built `testusb`, on the kernel `usbtest` driver and matching gadget firmware/configuration, and optionally on `DEVICE`. Risks are non-portability under strict POSIX `/bin/sh`, infinite execution by design, hidden `testusb` stderr, and manual configuration assumptions. Test signals are pass/fail exit status, case progress lines, and sustained operation under mixed system load.
