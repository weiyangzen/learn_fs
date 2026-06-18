<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c

## Purpose

This file implements the serdev UART transport for a ChromeOS Embedded Controller. It turns an ACPI-described or OF-described UART-attached EC into a `struct cros_ec_device`, provides packet transfer with the Chrome EC host packet format, and wires suspend/resume into the common EC core.

## Important APIs, Types, And Functions

The main private types are `struct response_info`, which tracks a pending EC response buffer, expected length, status, and wait queue, and `struct cros_ec_uart`, which stores the serdev device, baud rate, flow control, IRQ, and response state. `cros_ec_uart_rx_bytes()` is the serdev receive callback. `cros_ec_uart_pkt_xfer()` is the `ec_dev->pkt_xfer` implementation. `cros_ec_uart_acpi_probe()` extracts UART serial-bus settings and a GPIO IRQ from ACPI resources. Probe allocates `cros_ec_device`, installs serdev callbacks, opens the UART, applies baud/flow settings, and calls `cros_ec_register()`.

## Control Flow

Probe initializes response synchronization, reads ACPI transport details, binds the Chrome EC device to the serdev, and registers it with the common Chrome EC stack. During command transfer, `cros_ec_prepare_tx()` formats `ec_dev->dout`; the UART driver writes it with `serdev_device_write_buf()` and waits up to `EC_MSG_DEADLINE_MS`. Receive callbacks append bytes into `ec_dev->din`, learn the expected packet length from `struct ec_host_response`, and wake the waiter once header plus payload has arrived. The transfer path then checks EC result, input size, checksum, copies payload into `ec_msg->data`, and handles reboot delay for `EC_CMD_REBOOT_EC`.

## State And Persistence

Runtime state is per-device and volatile: the response buffer pointer is set only while a command is outstanding and cleared afterward to drop out-of-band bytes. The wait queue coordinates the transfer thread with receive callbacks. Persistent state is in the EC firmware and UART hardware, not in this driver. PM state is delegated to `cros_ec_suspend()` and `cros_ec_resume()`.

## Dependencies And Integration Points

The driver depends on serdev, ACPI serial-bus resources, optional OF compatible `google,cros-ec-uart`, Chrome EC protocol helpers, and the common `cros_ec_register()` device model. It publishes ACPI ID `GOOG0019` and an OF match table.

## Risks

Only one outstanding command is represented by `response_info`; concurrent transfers would corrupt shared response state if the common EC layer did not serialize access. The expected length is trusted from the EC response header before checksum validation, so oversize protection depends on `din_size`. ACPI probing is unconditional in probe, so OF-only systems without ACPI resources may fail despite an OF match. Short UART writes become `-EIO`, and fragmented responses rely on the fixed 500 ms deadline.

## Test Signals

Useful tests include probe with `GOOG0019`, correct baud/flow-control selection, IRQ delivery to the Chrome EC core, successful EC command exchange, checksum failure injection, oversize response handling, fragmented receive callbacks, reboot command timing, and suspend/resume over a UART-connected EC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c -->
