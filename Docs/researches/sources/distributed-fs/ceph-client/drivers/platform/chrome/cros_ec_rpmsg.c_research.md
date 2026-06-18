# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_rpmsg.c

## Purpose
`cros_ec_rpmsg.c` is the Chrome EC transport driver for ECs reachable over RPMsg. It adapts the generic `cros_ec_device` command callbacks to RPMsg packet exchange and converts RPMsg host-event notifications into normal Chrome EC IRQ processing.

## Important APIs, Types, and Functions
- `struct cros_ec_rpmsg_response` describes incoming RPMsg messages with a type byte and aligned payload.
- `struct cros_ec_rpmsg` stores the RPMsg device, endpoint, command completion, host-event work item, and probe/pending-event flags.
- `cros_ec_pkt_xfer_rpmsg()` sends v3 packets, waits up to 200 ms for completion, validates EC host response length and checksum, copies payload into the command, and handles reboot delay.
- `cros_ec_cmd_xfer_rpmsg()` returns `-EINVAL` because old protocol transfers are unsupported.
- `cros_ec_rpmsg_callback()` demultiplexes host-command responses and host events.
- Probe/remove/suspend/resume bind the transport into the generic Chrome EC core.

## Control Flow
Probe allocates a `cros_ec_device`, assigns `cmd_xfer`/`pkt_xfer`, creates an RPMsg endpoint, registers the EC core, then marks probe complete and drains any host event that arrived early. Command transfer prepares a v3 packet with `cros_ec_prepare_tx()`, sends it through `rpmsg_send()`, blocks on `xfer_ack`, parses `struct ec_host_response` from `ec_dev->din`, calls `cros_ec_check_result()`, validates `data_len <= insize`, computes checksum over header and data, and returns payload length. The RPMsg callback copies host-command payloads into `din` and completes the waiter; host-event messages either schedule work immediately or set a pending flag until registration completes.

## State and Persistence
Driver state is per RPMsg device and devm-managed except the endpoint, which is explicitly destroyed. `has_pending_host_event` persists only across the probe window. `probe_done` gates event handling to avoid invoking Chrome EC IRQ handling before the core registration is ready.

## Dependencies and Integration Points
It depends on Linux RPMsg, completions, workqueues, device tree match `"google,cros-ec-rpmsg"`, Chrome EC protocol helpers, and core functions `cros_ec_device_alloc()`, `cros_ec_register()`, `cros_ec_unregister()`, `cros_ec_suspend()`, `cros_ec_resume()`, and `cros_ec_irq_thread()`.

## Risks and Edge Cases
Only protocol v3 packet mode is supported, so fallback to v2 will fail. Incoming response length is truncated to `din_size` before completion, but checksum validation can still catch corrupted/truncated data. Timeout returns `-EIO`, not `-ETIMEDOUT`, which callers may treat as a generic transport failure. `has_pending_host_event` is a boolean, so multiple early host events collapse into one scheduled IRQ pass.

## Test Signals
There is no local KUnit suite for RPMsg in this subset. Useful validation comes from protocol KUnit tests for shared framing/check-result behavior and from runtime testing with RPMsg EC firmware that emits both command responses and host events.
