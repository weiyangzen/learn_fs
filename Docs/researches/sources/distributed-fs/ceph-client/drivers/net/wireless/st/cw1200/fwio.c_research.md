# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.c

Purpose: Firmware loading and hardware revision detection for CW1200/CW1x00 devices.

Important APIs and functions: Public entry point is `cw1200_load_firmware`. Internal helpers include `cw1200_get_hw_type`, `cw1200_load_firmware_cw1200`, `config_reg_read`, and `config_reg_write`.

Control flow: `cw1200_load_firmware` reads the config register, derives hardware type and major revision, writes and verifies DPLL based on reference clock, wakes the device, detects silicon cut by AHB ID reads, disables block ACK on old cuts, verifies access mode, loads firmware for supported HIF silicon, enables interrupt signaling, and switches from access mode to message/queue mode. `cw1200_load_firmware_cw1200` selects firmware and SDD file names by revision, initializes bootloader control registers, releases CPU reset/clock, requests the firmware blob, waits for bootloader readiness, writes firmware blocks into APB FIFO while polling `GET`, and waits for completion status.

State and persistence: Updates `priv->hw_type`, `priv->hw_revision`, `priv->sdd_path`, and block-ack masks. Firmware data is requested transiently for download and released after loading; SDD is loaded later by MAC setup.

Dependencies and integration: Uses `hwio` APB/AHB/register accessors, firmware loader API, DPLL helper from `main.c`, IRQ enable from BH/hwio, and firmware/SDD names from `fwio.h`.

Risks: Only `HIF_8601_SILICON` firmware load is implemented; CW1160/1260 is explicitly unsupported. Timeout and FIFO polling values are hardware-sensitive. Switching access/message mode and IRQ enable ordering are fragile. Some config read/write helpers ignore return values in default branches.

Test signals: Hardware boot with each supported cut, missing firmware files, malformed hardware config register, DPLL mismatch, bootloader timeout, FIFO backpressure, download error statuses, and startup indication after message mode.
