# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.c

## Purpose
Implements HDMI CEC support for the Synopsys HDMI receiver as a CEC framework adapter sharing the main HDMI receiver MMIO block through callback operations.

## Important APIs, Types, And Functions
The exported entry points are `snps_hdmirx_cec_register()` and `snps_hdmirx_cec_unregister()`. Internal CEC adapter operations are `hdmirx_cec_enable()`, `hdmirx_cec_log_addr()`, and `hdmirx_cec_transmit()`. The interrupt path is split into `hdmirx_cec_hardirq()` for status clearing/message extraction and `hdmirx_cec_thread()` for notifying the CEC core.

## Control Flow
Registration allocates `struct hdmirx_cec`, enables the CEC block, enables RX auto-ack, clears TX/interrupt state, allocates a CEC adapter with monitor support, requests a no-auto-enable threaded IRQ, registers the adapter, unmasks key CEC TX/RX interrupts, and enables the IRQ. Adapter enable resets logical addresses, optionally calls parent enable/disable hooks, toggles `CEC_ENABLE`, and masks/unmasks CEC interrupts.

Transmit writes byte count and up to four packed 32-bit data registers, then starts transmission. The hard IRQ clears interrupt status, maps TX done/NACK/arbitration/lane errors to CEC framework status, copies RX messages on end-of-message, locks the RX buffer, and wakes the threaded handler. The threaded handler reports completed transmit attempts and received messages to the CEC core.

## State And Persistence
State is in `struct hdmirx_cec`: logical-address bitmask, adapter pointer, current RX message, TX status, TX/RX completion booleans, IRQ number, parent pointer, and ops. Hardware state includes CEC address, interrupt masks/clears, TX/RX FIFOs, and CEC enable/config bits. No durable state is stored.

## Dependencies And Integration Points
Depends on `media/cec.h`, the main HDMIRX register definitions, Linux IRQ APIs, devm allocation, and parent callbacks for MMIO access. Userspace sees a normal CEC character device associated with the HDMI receiver device.

## Risks
The transmit path relies on the CEC core to pass valid message lengths. RX uses memory barriers between hard IRQ and threaded IRQ; changes to this path must preserve ordering. Interrupt clearing and RX buffer locking are hardware-specific and can drop messages if mishandled. Logical address programming always sets bit 15 along with the requested address, which should be checked against the hardware manual when changing addressing behavior.

## Test Signals
CEC adapter registration under `/dev/cec*`, logical address allocation, `cec-ctl` ping/transmit tests, monitor-all receive behavior, TX status reporting for ACK/NACK/arbitration loss, plug/unplug with parent IRQ disable ordering, and suspend/resume behavior through the main driver are useful validation signals.
