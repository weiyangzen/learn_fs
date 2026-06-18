# sources/distributed-fs/ceph-client/drivers/net/phy/as21xxx.c

## Purpose
Implements Aeonsemi AS21xxx 10G/5G/2.5G Clause 45 PHY support. The driver handles pre-firmware generic ID matching, firmware loading, IPC command synchronization, status decoding through mapped Clause 22 registers, PTP clock enable, rate-adaptation configuration, and LED hardware controls.

## Important APIs, Types, and Functions
Important state is `struct as21xxx_priv`, which stores IPC parity and a mutex protecting IPC access. Firmware and IPC functions include `aeon_firmware_load`, `aeon_firmware_boot`, `aeon_ipc_send_cmd`, `aeon_ipc_send_msg`, `aeon_ipc_sync_parity`, `aeon_ipc_get_fw_version`, and `aeon_dpc_ra_enable`. PHY callbacks include `as21xxx_probe`, `as21xxx_match_phy_device`, `as21xxx_read_status`, `as21xxx_led_brightness_set`, `as21xxx_led_hw_is_supported`, `as21xxx_led_hw_control_get`, `as21xxx_led_hw_control_set`, and `as21xxx_led_polarity_set`.

## Control Flow and State
Before firmware is loaded, devices expose the generic `PHY_ID_AS21XXX`. The first driver entry uses `as21xxx_match_phy_device` to detect Aeonsemi vendor IDs, load firmware from the `firmware-name` property, synchronize IPC parity using two NOOP commands, and then return so the newly exposed exact PHY ID can match a real driver entry. Normal probe allocates private state, initializes the mutex, synchronizes IPC, logs firmware version, enables PTP clock, and enables DPC rate adaptation. Status reads link through mapped C22-in-C45 registers, avoids reporting link while BMCR autoneg restart is set, reads LPA including 1000Base-T status from mapped registers, resolves autoneg linkmode, or decodes forced speed from a vendor speed register.

## Dependencies and Integration Points
Depends on firmware loader APIs, Open Firmware `firmware-name`, Clause 45 phylib MMD access, mapped Clause 22 registers in the AN MMD, MDIO module matching, mutex protection for IPC, phylib LED callbacks, PTP-clock vendor bit, and ethtool netdev trigger definitions.

## Risks and Test Signals
Risks include firmware load in `match_phy_device` being unusual and order-sensitive, IPC parity desynchronization, firmware-reported return size overruns guarded but still hardware-dependent, unsupported firmware alignment, an apparent speed-switch mask typo using `VEND1_SPEED_STATUS` instead of `VEND1_SPEED_MASK`, and LED index checks using `>` instead of `>=` for `AEON_MAX_LEDS`. Test signals include cold-boot generic-ID probe, firmware load and exact-ID rematch, IPC firmware version log, autoneg and forced speed reporting, master/slave failure paths, LED trigger validation, PTP clock enable readback, and concurrent LED/status operations while IPC is active.
