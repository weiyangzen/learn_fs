<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c

## Purpose
`hdmi4_cec.c` implements the optional OMAP4 HDMI CEC adapter using the Linux CEC framework. It programs the HDMI core CEC register block, receives and transmits CEC messages, manages logical addresses, enables or disables CEC clocks and IRQs, and maps hardware completion/error events to CEC framework callbacks.

## Important APIs, types, and functions
External functions are `hdmi4_cec_init()`, `hdmi4_cec_uninit()`, `hdmi4_cec_irq()`, and `hdmi4_cec_set_phys_addr()`. Adapter callbacks are `hdmi_cec_adap_enable()`, `hdmi_cec_adap_log_addr()`, and `hdmi_cec_adap_transmit()`. Helper paths include `hdmi_cec_received_msg()`, `hdmi_cec_clear_tx_fifo()`, and `hdmi_cec_clear_rx_fifo()`.

## Control flow
Initialization allocates a CEC adapter with transmit, logical-address, passthrough, and remote-control capabilities, stores the HDMI wrapper pointer in `core->wp`, disables the CEC clock divider initially, and registers the adapter. Enabling CEC powers the HDMI core through `hdmi4_core_enable()`, configures the wrapper CEC clock divider for 2 MHz, clears TX and RX FIFOs, clears pending CEC interrupts, enables wrapper core IRQs, unmasks core CEC IRQ bit 3, enables CEC TX/RX/retry interrupts, and runs CEC calibration. Disable reverses IRQ masks, clears wrapper core IRQ state, disables the CEC clock, and powers down the core reference.

Transmit clears the TX FIFO, clears TX interrupt status, programs retry count, initiator, destination, opcode, operands, and operand count. IRQ handling acknowledges both CEC status registers, reports transmit success or NACK/max-retry completion through `cec_transmit_done()`, clears TX state, and drains received messages through `cec_received_msg()`.

## State and persistence
CEC state is stored in the Linux `cec_adapter` referenced by `core->adap`, the physical address programmed through `cec_s_phys_addr()`, logical address masks in HDMI CEC CA registers, FIFO contents, interrupt masks, retry count, and CEC clock divider. The adapter persists from HDMI component bind until unbind.

## Dependencies and integration points
The file depends on `hdmi.h` register helpers, HDMI4 core power helpers, wrapper IRQ enable helpers, and the Linux media CEC framework. `hdmi4.c` calls `hdmi4_cec_irq()` from the HDMI core interrupt path and updates physical address after EDID reads or disconnects.

## Risks
CEC is clock and power sensitive: enabling CEC increments HDMI core power and must disable the divider and core on failure. FIFO-clear loops are bounded by retry counts but do not sleep, so bad hardware state can return `-EIO`. Receive length is clamped to fit `CEC_MAX_MSG_SIZE`, but malformed FIFO state can still discard frames. The transmit path returns immediately after programming hardware, relying on IRQ completion; lost IRQs would stall framework completion.

## Test signals
Useful signals include adapter registration, enabling/disabling CEC via userspace, logical address programming, physical address updates after EDID and disconnect, successful ping and opcode transmission, NACK/max-retry reporting, received message delivery, CEC clock divider programming, and operation across HDMI hotplug and display power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c -->
