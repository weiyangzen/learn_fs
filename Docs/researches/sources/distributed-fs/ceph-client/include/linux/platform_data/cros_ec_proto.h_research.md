
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_proto.h

## Purpose
This header defines the Linux-side protocol interface for ChromeOS EC devices. It wraps the raw command ABI from `cros_ec_commands.h` in kernel device structures, transport hooks, platform naming, transfer helpers, event notifiers, and command buffer metadata used by ChromeOS EC MFD children and transport drivers.

## Important APIs And Types
The core request object is `struct cros_ec_command`, with command version, command id, outgoing size, maximum incoming size, result code, and flexible payload buffer. `struct cros_ec_device` is the transport/device state: physical name, device/class pointers, optional memory-map reader, size limits, private transport data, IRQ, aligned input/output buffers, wake/suspend/registration flags, `cmd_xfer` and `pkt_xfer` transport callbacks, mutex serialization, MKBP support, host sleep metadata, event and panic notifier heads, and child platform devices for main EC and PD. `struct cros_ec_platform` carries MFD platform naming and command offset, while `struct cros_ec_dev` is the class-facing EC device wrapper with debugfs, feature cache, and command offset. Exported helpers include `cros_ec_prepare_tx()`, `cros_ec_check_result()`, `cros_ec_cmd_xfer()`, and `cros_ec_cmd_xfer_status()`.

## Control Flow, State, And Persistence
The header describes synchronous command flow: callers populate `cros_ec_command`, transport code prepares protocol bytes, sends with `cmd_xfer` or `pkt_xfer`, then checks EC result separately from bus errors. The device mutex enforces one transaction at a time. Persistent runtime state includes probed protocol version, max request/response/passthrough sizes, wake state, suspend state, cached feature bits, last host sleep result, host event wake mask, MKBP event payload, and event timestamps.

## Dependencies And Integration Points
It includes Linux device, mutex, lockdep, notifier, and ChromeOS EC command ABI headers. It is the shared contract among EC physical transports such as LPC/I2C/SPI/ISH, the MFD core, EC char/debug interfaces, PD child devices, MKBP input/event handling, suspend/resume code, and panic notification consumers.

## Risks And Test Signals
The main risks are buffer sizing against transport overhead, unaligned payload handling, command result confusion with transport errors, notifier ordering during suspend/resume, and stale cached protocol limits after EC reboot. Test signals include successful feature probing, command transfer under each transport, command-status helper behavior for non-success EC results, MKBP event notifier delivery, wake mask behavior across suspend, and EC reboot/interface-ready re-query.
