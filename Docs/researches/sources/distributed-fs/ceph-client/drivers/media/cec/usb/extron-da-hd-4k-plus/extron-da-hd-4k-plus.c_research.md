# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/extron-da-hd-4k-plus.c

## Purpose
This is a serio-based driver for Extron DA HD 4K Plus HDMI splitters. It manages the device over the Extron serial protocol, exposes one CEC adapter per HDMI input/output port, exposes V4L2 EDID controls per port, and optionally manages splitter CEC policy internally.

## Important APIs, Types, and Functions
Core protocol helpers are `extron_send_byte`, `extron_send_len`, `extron_send_and_wait_len`, and `extron_interrupt`. EDID helpers include `extron_parse_edid`, `extron_update_edid`, `extron_write_edid`, `extron_read_edid`, and `update_edid_work`. CEC callbacks are `extron_cec_adap_enable`, `extron_cec_adap_log_addr`, `extron_cec_adap_transmit`, configuration callbacks, canceled-transmit callback, status callback, and received-message callback. V4L2 ioctl handlers implement querycap, input/output enumeration, EDID get/set, and log status.

## Control Flow
Serio connect allocates global state, registers a V4L2 device, opens serio, and starts a setup kthread. The setup thread waits for command responsiveness, queries model/name/firmware/type/CEC engine, configures HPD behavior, allocates ports/adapters/video devices, enables CEC manual mode, initializes logical addresses, queries signal/EDID states, registers video devices and CEC adapters, optionally sets driver-managed log addresses, and then polls once per second. The interrupt parser accumulates CR/LF-delimited replies, dispatches signal/HDCP/CEC/physical-address/EDID events, and completes synchronous command waits.

## State and Persistence
`struct extron` holds serial connection, port arrays, unit metadata, V4L2 device, EDID serialization state, command reply buffers, and setup thread. `struct extron_port` holds per-port CEC/V4L2 state, EDID buffers, control state, queued RX messages, TX completion status, physical address, hotplug/signal flags, and splitter-port policy. Persistent device state can be changed through Extron commands for CEC enable/manual mode, logical addresses, HPD behavior, and written EDID.

## Dependencies and Integration Points
The driver binds to `SERIO_EXTRON_DA_HD_4K_PLUS`, uses CEC core, V4L2 controls and EDID ioctls, serio, kthreads, workqueues, completions, and local splitter policy. Module parameters tune debug, CEC vendor ID, EDID manufacturer name, and HPD behavior.

## Risks and Test Signals
This driver has many asynchronous paths: command completion, serio interrupt parsing, per-port workqueues, setup thread, delayed EDID work, and disconnect cleanup. EDID writes always upload 256 bytes even for one-block sources. Tests should cover unsupported model/firmware rejection, power-up delay path, disconnect during setup or EDID read, malformed serial replies, RX queue overflow, V4L2 EDID get/set, HPD state changes, physical address updates, manual vs vendor-managed CEC modes, and splitter polling.
