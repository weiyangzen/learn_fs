# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.c

Purpose: implements the standalone CEC adapter driver for classic DesignWare HDMI blocks. It bridges Linux CEC framework operations to DW-HDMI CEC registers through parent-provided read/write/enable/disable callbacks.

Important APIs/types/functions: `struct dw_hdmi_cec` stores parent HDMI pointer, CEC ops, logical address mask, CEC adapter, RX message, TX status flags, notifier, IRQ, and suspend-saved interrupt register values. `dw_hdmi_cec_log_addr()` programs logical/broadcast addresses. `dw_hdmi_cec_transmit()` writes up to 16 TX bytes, count, and control mode based on signal-free time. `dw_hdmi_cec_hardirq()` acknowledges CEC status, maps DONE/NACK/ARBLOST/ERROR to CEC TX statuses, reads RX frames on EOM, and wakes the threaded handler. `dw_hdmi_cec_thread()` reports transmit completion and received messages to the CEC core. Probe allocates/registers the adapter, requests IRQ, registers a CEC notifier, and registers the adapter.

Control flow: probe initializes hardware to masked/idle, allocates a CEC adapter with default capabilities and connector info, installs cleanup for failed probe, requests shared threaded IRQ, registers notifier, then registers adapter. Adapter enable unmasks selected CEC status bits, clears lock/status, resets logical addresses, and calls parent enable; disable masks interrupts, clears polarity, and calls parent disable. Suspend caches polarity/mask/mute registers; resume restores logical addresses and those registers.

State and persistence: logical address bits persist in `cec->addresses` and are restored after resume. RX/TX completion flags are handed from hard IRQ to thread. Suspend state stores three interrupt-control registers. Hardware FIFOs/status/lock are volatile.

Dependencies and integration: depends on `dw-hdmi-cec.h` platform data, Linux CEC core, CEC notifier, DRM EDID include, platform device framework, and parent DW-HDMI register callbacks. Userspace sees a CEC chardev associated with the parent HDMI device.

Risks: hard IRQ and thread share booleans/message without a lock, relying on IRQ threading and barriers around RX data. RX reads all available bytes but clamps oversize frames. Probe error after notifier registration unregisters notifier only on adapter registration failure. A formatting anomaly leaves leading spaces in suspend assignments but compiles. Parent callbacks must be valid during IRQ handling and suspend/resume.

Test signals: CEC adapter registration, logical address allocation/clear, transmit outcomes for OK/NACK/arbitration lost/error, receive EOM frames of 1-16 bytes, enable/disable masking, suspend/resume retaining addresses, and shared IRQ behavior when no CEC status is pending.
