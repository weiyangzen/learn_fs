# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/cros-ec-cec.c

Purpose: This platform driver exposes ChromeOS Embedded Controller CEC ports as Linux CEC adapters. It translates EC MKBP events and host commands into CEC core receive/transmit/logical-address/enable operations and associates each EC port with a DRM connector via DMI/PCI tables.

Important APIs, types, and functions: `struct cros_ec_cec_port` stores EC port number, adapter, notifier, RX message, and parent pointer. `struct cros_ec_cec` stores EC device, notifier block, write command version, port count, and port array. Key functions include message/event handlers (`handle_cec_message()`, `cros_ec_cec_read_message()`, `handle_cec_event()`, `cros_ec_cec_event()`), CEC ops (`cros_ec_cec_set_log_addr()`, `cros_ec_cec_transmit()`, `cros_ec_cec_adap_enable()`), PM ops, DMI connector matching, EC capability queries (`cros_ec_cec_get_num_ports()`, `cros_ec_cec_get_write_cmd_version()`), per-port init, probe, and remove.

Control flow and state: Probe finds the HDMI DRM device and connector list from DMI/PCI tables, allocates driver state, enables wakeup, queries EC port count with fallback to one port on old firmware, determines whether write command v1 is supported, initializes each port by allocating/registering a one-LA adapter and notifier, then registers an EC event notifier. EC events either report old single-port inline messages, multi-port event bitmasks, transmit OK/failure, or data-ready; data-ready triggers `EC_CMD_CEC_READ_MSG`. Transmits send `EC_CMD_CEC_WRITE_MSG` using v0 single-port payload or v1 port-aware payload. Enable and logical-address changes use `EC_CMD_CEC_SET`.

State and persistence behavior: Runtime state is volatile and mirrors EC firmware capabilities: number of ports and write command version. Logical address and enabled state are set in the EC but not persisted by this driver. Connector mapping is static DMI table data.

Dependencies and integration points: Depends on ChromeOS EC device/protocol, EC MKBP event notifier, platform device parent data, DMI/PCI lookup, CEC core/notifier, and PM wake IRQ handling. DMI tables must match hardware connector ordering to EC port numbering.

Risks and edge cases: Hardware support is table-driven; unsupported systems return `ENODEV` after warning. Old firmware supports one port and old message events; multi-port firmware needs command v1. Event port bounds must be enforced. The EC firmware handles retries, so failures are reported with `MAX_RETRIES` to prevent duplicate core retries. Probe cleanup must unregister only successfully registered ports.

Test signals: Test supported DMI systems with one and multiple ports, old and new EC firmware, transmit OK/failure events, receive data-ready flow, inline old message events, invalid port events, logical-address/enable commands, suspend/resume wake IRQ, connector info propagation, and remove after partial probe failure.
