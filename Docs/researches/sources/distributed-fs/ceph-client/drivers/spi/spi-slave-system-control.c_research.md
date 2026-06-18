# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-system-control.c

## Purpose

`spi-slave-system-control.c` is a SPI target protocol handler that lets a remote SPI host request system reboot, poweroff, halt, or suspend by sending one of four two-byte big-endian command values. It is intentionally small and policy-heavy: received SPI data directly triggers kernel system-control APIs.

## Important APIs, Types, and Functions

`struct spi_slave_system_control_priv` stores the bound `spi_device`, a `finished` completion, one reusable `spi_transfer`, one `spi_message`, and a big-endian 16-bit command buffer. `spi_slave_system_control_submit()` initializes the reusable one-transfer message, installs the completion callback, and queues it with `spi_async()`. `spi_slave_system_control_complete()` decodes the command and calls `kernel_restart()`, `kernel_power_off()`, `kernel_halt()`, or `pm_suspend(PM_SUSPEND_MEM)`. Probe allocates state, sets the RX buffer, submits the first asynchronous receive, and stores drvdata. Remove calls `spi_target_abort()` and waits for the callback to complete.

## Control Flow

The handler keeps exactly one asynchronous RX message outstanding. When a two-byte message completes successfully, the callback converts `priv->cmd` with `be16_to_cpu()`, executes the matching system action, and then resubmits another receive. Any SPI message error or resubmit failure terminates the loop by completing `finished`. Removal aborts the target-side controller transaction and waits until the callback observes termination.

## State and Persistence Behavior

There is no persistent storage. State is limited to the reusable SPI message/transfer and the last received command. The side effects are system-wide and potentially persistent outside the driver: reboot modes, power state changes, and suspend state are controlled by kernel system-control paths.

## Dependencies and Integration Points

The file depends on the SPI target-device API, completions, reboot/poweroff/halt APIs, and system suspend support. It must run on a SPI controller that supports target mode and `spi_target_abort()`.

## Risks and Edge Cases

Any entity able to send the magic two-byte values on the SPI link can reboot, power off, halt, or suspend the machine. There is no authentication, framing beyond two bytes, rate limit, or confirmation. Calling reboot or suspend APIs from an SPI completion callback may run in a context where sleeping behavior depends on SPI core completion threading. Unknown commands only warn and resubmit. Remove can wait indefinitely if the controller's `target_abort` fails to complete the outstanding message.

## Test Signals

Tests should cover all four command values in big-endian order, unknown commands, repeated commands, SPI completion error, resubmit failure, driver removal while an RX is pending, and target controller abort behavior. Security review should treat this as a privileged hardware management interface, not a general-purpose remote-control protocol.
