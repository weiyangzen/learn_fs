<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.h -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_device.h

## Purpose
Declares the HSR/PRP virtual device setup, finalization, port cleanup, carrier/operstate, and MTU helper APIs.

## APIs, Types, and Functions
Declares `hsr_del_ports()`, `hsr_dev_setup()`, `hsr_dev_finalize()`, `hsr_check_carrier_and_operstate()`, and `hsr_get_max_mtu()`.

## Control Flow, State, and Persistence
No executable logic is present. The declarations expose device lifecycle operations to the netlink creation path, slave teardown path, and event notification path.

## Dependencies and Integration
Depends on `linux/netdevice.h` and `hsr_main.h` for `struct hsr_priv`, port types, and protocol constants. Implemented in `hsr_device.c` and consumed by `hsr_main.c`, `hsr_netlink.c`, and other HSR peers.

## Risks and Test Signals
Risks are header/API drift between implementation and callers, especially around `hsr_dev_finalize()` arguments for optional interlink/RedBox and extack reporting. Test signals are clean builds across HSR netlink creation, slave unregister, and notifier code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.h -->
