# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.c

## Purpose
This is the framework-facing Samsung S5P HDMI CEC platform driver. It allocates/registers the CEC adapter, handles runtime PM, maps IRQs to CEC core notifications, and delegates register operations to `exynos_hdmi_cecctrl.c`.

## Important APIs, Types, and Functions
CEC callbacks are `s5p_cec_adap_enable`, `s5p_cec_adap_log_addr`, and `s5p_cec_adap_transmit`. IRQ work is split between `s5p_cec_irq_handler` and `s5p_cec_irq_handler_thread`. Probe/remove and runtime PM are implemented with `s5p_cec_probe`, `s5p_cec_remove`, `s5p_cec_runtime_suspend`, and `s5p_cec_runtime_resume`.

## Control Flow
Probe parses the HDMI phandle, allocates state, requests IRQ, obtains the `hdmicec` clock, gets the PMU syscon, maps registers, allocates a CEC adapter, registers a notifier, registers the adapter, and enables runtime PM. Enabling resumes the device, resets hardware, programs divider/filter, unmasks interrupts, and enables RX. Disabling masks interrupts and drops runtime PM. Hard IRQ snapshots status and sets `cec->tx`/`cec->rx`; the thread calls `cec_transmit_done` or `cec_received_msg`.

## State and Persistence
`struct s5p_cec_dev` stores TX/RX state enum values, one RX `cec_msg`, clock, PMU regmap, notifier, IRQ, and mapped registers. Runtime PM controls clock lifetime. No durable configuration is stored.

## Dependencies and Integration Points
The driver integrates with platform resources, OF compatible `samsung,s5p-cec`, CEC notifier connector data, `pm_runtime`, `syscon_regmap_lookup_by_phandle`, and local register helpers. The optional `needs-hpd` DT property adds `CEC_CAP_NEEDS_HPD`.

## Risks and Test Signals
RX overrun is only logged if the worker has not consumed the previous message. TX retry count is forced to at least one. Test runtime suspend/resume, HPD-required capability, TX done/NACK/error mapping, RX error reset, message length clamping, and cleanup paths when notifier or adapter registration fails.
