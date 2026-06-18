# sources/distributed-fs/ceph-client/drivers/net/phy/air_en8811h.c

## Purpose
Implements Airoha EN8811H and AN8811HB 2.5G PHY support. The driver loads required MD32 firmware, accesses internal PBUS registers through an MDIO page window, configures SerDes polarity, exposes hardware LED controls, registers optional clock outputs, handles rate matching, and decodes link status.

## Important APIs, Types, and Functions
The private state `en8811h_priv` stores firmware version, MCU restart state, three LED states/rules, a `clk_hw`, associated `phy_device`, and saved clock-output state. Important functions include PBUS helpers `air_buckpbus_reg_read`, `air_buckpbus_reg_write`, `air_buckpbus_reg_modify`, firmware loaders `en8811h_load_firmware` and `an8811hb_load_firmware`, `en8811h_wait_mcu_ready`, CRC helper `an8811hb_check_crc`, probe functions for both chips, config-init functions for both chips, LED callbacks `air_led_blink_set`, `air_led_brightness_set`, `air_led_hw_control_set/get`, clock ops for both variants, `en8811h_config_aneg`, `en8811h_read_status`, `en8811h_clear_intr`, and `en8811h_handle_interrupt`.

## Control Flow and State
Probe allocates private state, loads firmware from chip-specific files, marks required MMDs present because MDIO_DEVS registers are empty, initializes default LED rules, registers a clock provider when common clock support is enabled, and configures LED GPIO pins as outputs. Config-init restarts the MCU on later invocations, programs EN8811H mode 1 for 2500Base-X rate adaptation, applies SerDes polarity from generic or legacy properties, and enables user-defined LED mode. AN8811HB uses separate polarity registers and firmware CRC checks. Link status uses generic link update and AN reads, adds 2.5G LP ability from standard or vendor registers, resolves pause, reads actual speed from `AIR_AUX_CTRL_STATUS`, forces full duplex, and sets `RATE_MATCH_PAUSE`.

## Dependencies and Integration Points
Depends on firmware files declared with `MODULE_FIRMWARE`, phylib C45 helpers, page-select support, LED netdev trigger APIs, PHY common polarity properties, common clock framework, device properties, unaligned little-endian firmware writes, and MDIO vendor MMD/PBUS register access. The driver integrates with MACs through rate matching and 2500Base-X/SerDes configuration.

## Risks and Test Signals
Risks include missing firmware causing probe failure, MDIO page restore bugs around PBUS access, long MCU-ready polling, firmware-version conditionals for 2.5G LP ability, divergent EN8811H versus AN8811HB polarity semantics, LED state/rules drifting after manual brightness/blink operations, and global `clk_save_context`/`clk_restore_context` affecting unrelated clocks. Test signals include firmware load logs and version reads, 10/100/1000/2500 full-duplex links, autoneg-disabled rejection, link interrupts, LED hardware-control triggers, clock-output enable/rate tests, suspend/resume, and polarity property validation.
