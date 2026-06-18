# sources/distributed-fs/ceph-client/include/linux/hsi/ssi_protocol.h

## Purpose
`hsi/ssi_protocol.h` declares helper hooks for SSIP slave support on top of the HSI core. It coordinates slave/master relationships, TX start/stop, reset events, running state, and wake-test control.

## Important APIs, Types, And Functions
The file declares `ssip_slave_get_master()`, `ssip_slave_start_tx()`, `ssip_slave_stop_tx()`, `ssip_reset_event()`, `ssip_slave_running()`, and `ssi_waketest()`. `ssip_slave_put_master()` is currently an empty inline helper. All APIs operate on `struct hsi_client *`.

## Control Flow And State
Slave protocol clients obtain their master client, request TX start/stop through the master, notify reset events, query running state, and optionally enable wake-test behavior. State is owned by the SSIP implementation and HSI client driver data, not this header.

## Dependencies And Integration Points
It includes `linux/hsi/hsi.h` and integrates with HSI client drivers implementing SSIP master/slave protocols.

## Risks
Risks include null or stale master pointers, unbalanced get/put semantics because `ssip_slave_put_master()` is a no-op, TX state races around reset, and callers assuming wake-test exists on all controllers.

## Test Signals
Test slave/master lookup, start/stop TX sequencing, reset event delivery, running-state transitions, wake-test toggling, and remove paths with outstanding master references.
