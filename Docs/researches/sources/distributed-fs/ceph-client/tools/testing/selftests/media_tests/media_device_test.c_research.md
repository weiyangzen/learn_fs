# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_test.c

Purpose: long-running media controller ioctl loop intended to be run while hardware is removed, unbound, or rebound.

Important APIs/types/functions: parses `-d`, uses `MEDIA_IOC_DEVICE_INFO`, `struct media_device_info`, random iteration count from `rand()`, and kselftest skip for non-root.

Control flow: requires root, opens the device once, prints operator instructions, then loops `count` times, issuing `MEDIA_IOC_DEVICE_INFO` every ten seconds and printing either errors or model/driver.

State and persistence: holds one media device FD open while external hot-unplug/unbind operations mutate device state.

Dependencies and integration points: hardware media controller, root, manual operator actions, optional KASAN/dmesg monitoring.

Risks: random iteration count may be extremely large; no signal cleanup needed but test duration is unpredictable. It does not fail on ioctl errors, because errors during removal may be expected.

Test signals: absence of kernel UAF/oops during external disruption is the real signal; program output is diagnostic.
