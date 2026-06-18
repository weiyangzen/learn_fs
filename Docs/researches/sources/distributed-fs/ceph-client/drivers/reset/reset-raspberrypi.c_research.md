# sources/distributed-fs/ceph-client/drivers/reset/reset-raspberrypi.c

Purpose: Raspberry Pi firmware reset provider, currently implementing the Pi 4 VL805/xHCI reset notification through VideoCore firmware.

Important APIs/types/functions: `struct rpi_reset` stores the reset controller and firmware handle. `rpi_reset_reset()` handles `RASPBERRYPI_FIRMWARE_RESET_ID_USB`, builds the hardwired PCI device address, calls `rpi_firmware_property(... RPI_FIRMWARE_NOTIFY_XHCI_RESET ...)`, and delays for VL805 startup. `rpi_reset_probe()` finds the parent firmware node, gets `struct rpi_firmware`, and registers `rpi_reset_ops`.

Control flow: probe defers until firmware is available, then exposes `RASPBERRYPI_FIRMWARE_RESET_NUM_IDS`. Consumers issue a reset pulse; unsupported IDs return `-EINVAL`.

State and persistence: only runtime firmware handle state exists. The reset itself delegates persistent hardware sequencing and optional VL805 firmware loading to VideoCore.

Dependencies and integration: integrates OF platform probing, the Raspberry Pi firmware mailbox API, reset-controller consumers, and `raspberrypi,firmware-reset` bindings.

Risks and test signals: the PCI address is hardcoded for Pi 4 topology and would be wrong for different wiring. Firmware call failures propagate directly. Test signals include probe deferral without firmware, USB reset success on Pi 4, unsupported-ID rejection, and xHCI recovery after PCI reset.
