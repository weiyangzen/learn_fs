# sources/distributed-fs/ceph-client/samples/rpmsg/rpmsg_client_sample.c

## Purpose

This module is a minimal rpmsg client driver. It binds to channels named `rpmsg-client-sample`, sends an initial message to the remote processor, and replies to each received message until a configurable receive count is reached.

## Important APIs, Types, and Functions

The driver defines module parameter `count`, per-instance `struct instance_data { int rx_count; }`, `rpmsg_sample_probe()`, `rpmsg_sample_cb()`, and `rpmsg_sample_remove()`. It uses `rpmsg_send()`, `devm_kzalloc()`, `dev_set_drvdata()`, `dev_get_drvdata()`, `print_hex_dump_debug()`, and `module_rpmsg_driver()`.

## Control Flow

Probe logs the channel source/destination, allocates instance data, stores it on the rpmsg device, and sends `"hello world!"`. The callback increments `rx_count`, hex-dumps the payload at debug level, stops replying once the count threshold is reached, otherwise sends another hello message. Remove only logs device removal.

## State and Persistence Behavior

Persistent state is per-bound-device `rx_count`; it is devm-managed and tied to the rpmsg device lifecycle. The module parameter `count` is writable through sysfs mode `0644` and controls future callback behavior.

## Dependencies and Integration Points

It depends on the rpmsg framework, a remote processor endpoint publishing the matching channel, and transport-specific endpoint creation.

## Risks and Edge Cases

If the remote side echoes immediately, this forms a ping-pong loop until `count`. Send failures are logged but do not unregister the driver. `count <= 0` effectively disables reply after the first receive because `rx_count >= count`.

## Test Signals

Bind against a remoteproc sample service, check dmesg for probe and incoming message logs, verify the receive count stops replies, and inspect dynamic debug output for payload dumps.
