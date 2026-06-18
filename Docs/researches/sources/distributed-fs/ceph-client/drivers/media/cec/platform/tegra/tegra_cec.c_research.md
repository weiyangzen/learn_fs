# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.c

## Purpose
This is the NVIDIA Tegra HDMI CEC driver for Tegra114/124/210. It registers a CEC adapter using a memory-mapped hardware engine with interrupt-driven TX FIFO feeding and RX byte collection.

## Important APIs, Types, and Functions
`struct tegra_cec` holds adapter, device, clock, MMIO base, notifier, IRQ, TX/RX completion flags, status, RX byte buffer/count, and TX register words/counts. CEC callbacks are `tegra_cec_adap_enable`, `tegra_cec_adap_log_addr`, `tegra_cec_adap_monitor_all_enable`, and `tegra_cec_adap_transmit`. `tegra_cec_error_recovery` resets hardware control and clears interrupts.

## Control Flow
Probe parses HDMI phandle, requests/remaps memory, gets/enables the `cec` clock, requests threaded IRQ, allocates/registers notifier and adapter, and supports monitor-all capability. Enable clears control/masks/status, programs filter and RX/TX timing constants, enables relevant interrupts, and sets TX/RX mode. Transmit builds per-byte TX register words with start/EOM/broadcast/retry bits and enables TX-register-empty interrupts. The hard IRQ handles underrun, arbitration, bus anomaly, frame transmitted/NACK, FIFO empty, and RX start/full; the thread reports CEC core completions.

## State and Persistence
TX/RX buffers and flags are in driver memory. Logical address bits and snoop mode live in `TEGRA_CEC_HW_CONTROL`. Timing and interrupt state are hardware registers. There is no persistent configuration.

## Dependencies and Integration Points
DT compatibles are `nvidia,tegra114-cec`, `nvidia,tegra124-cec`, and `nvidia,tegra210-cec`. The driver integrates with platform resources, `cec-notifier`, Tegra clocking, and optional legacy platform PM callbacks.

## Risks and Test Signals
IRQ status handling returns early for several TX errors before clearing the specific interrupt through the normal path, relying on recovery. RX overflow interrupt is defined but not enabled/handled. Suspend only disables the clock and resume only reenables it, without restoring hardware configuration. Test FIFO underrun, arbitration/bus anomaly, NACK, RX EOM collection, monitor-all toggling, logical address invalidation, and suspend/resume adapter re-enable.
