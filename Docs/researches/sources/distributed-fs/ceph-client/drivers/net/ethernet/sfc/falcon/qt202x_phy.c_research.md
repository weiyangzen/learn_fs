# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/qt202x_phy.c

## Purpose
`qt202x_phy.c` implements the `ef4_phy_operations` backend for AMCC/Quake QT202x SFP+/XFP PHYs, including QT2022C2 and QT2025C variants. It handles PHY probe/init/reset, firmware readiness, QT2025C mode switching, link polling, TX-disable/loopback reconfiguration, module EEPROM exposure, LED control, and PHY-private cleanup.

## Important APIs, Types, And Functions
The public helper `falcon_qt202x_set_led()` writes Quake LED mode registers. Private `struct qt202x_phy_data` stores the last PHY mode, bug-17190 workaround state/timer, and QT2025C firmware version. Firmware/reset helpers include `qt2025c_wait_heartbeat()`, `qt2025c_wait_fw_status_good()`, `qt2025c_restart_firmware()`, `qt2025c_wait_reset()`, and `qt2025c_firmware_id()`. Link recovery and mode control are handled by `qt2025c_bug17190_workaround()` and `qt2025c_select_phy_mode()`. The operation table uses `qt202x_phy_probe()`, `qt202x_phy_init()`, `qt202x_phy_reconfigure()`, `qt202x_phy_poll()`, `qt202x_phy_get_link_ksettings()`, `qt202x_phy_remove()`, `qt202x_phy_get_module_info()`, and `qt202x_phy_get_module_eeprom()`.

## Control Flow
Probe allocates PHY-private state, sets required MMDs, declares Clause 45/C22-emulation support, and publishes supported loopbacks. Init resets the PHY, performs board-specific PHY initialization, reads/logs PHY ID, and records QT2025C firmware information. QT2025C reset waits for firmware heartbeat and good microcontroller status, with a one-time firmware restart workaround if status stalls. Reconfigure optionally switches QT2025C operating mode based on loopback, applies static TX disable for low-power or loopback cases, or resets older QT202x PHYs when TX is re-enabled, then calls common MDIO loopback reconfiguration. Poll updates 10G full-duplex link state and runs the QT2025C PCS-stuck workaround.

## State And Persistence
The driver persists private state in `efx->phy_data`. Hardware state is persisted through MDIO writes to PMA/PMD and PCS vendor registers, LED registers, TX static-disable bits, loopback bits, operating-mode registers, firmware control registers, and module EEPROM windows. Link state is stored in `efx->link_state`, and supported loopbacks/MMD masks are set during probe.

## Dependencies And Integration Points
The file depends on Linux slab/timer/delay APIs, `efx.h`, common MDIO helpers, `phy.h`, and `nic.h`. It integrates with board revision data through `falcon_board(efx)`, with generic PHY/link code through `falcon_qt202x_phy_ops`, with ethtool through link settings and module EEPROM/info callbacks, and with common MDIO liveness/settings helpers.

## Risks
The QT2025C mode-switch sequence is a long vendor-specific register script that varies by board revision; mistakes can break firmware/module I2C recovery or leave the PHY in the wrong operating mode. Timeouts around heartbeat and firmware status are hardware-sensitive and include user-facing diagnostics for non-compliant direct-attach cables. The bug-17190 workaround deliberately toggles PMA/PMD loopback after a persistent bad state; false positives could disturb link. EEPROM reads are byte-by-byte MDIO operations and rely on the correct MMD/base for the PHY variant.

## Test Signals
Signals include successful probe allocation and MMD mask setup, PHY reset completion, firmware version log for QT2025C, mode switching when entering/leaving loopback, TX disable under low-power or loopback, stable 10G full-duplex link polling, recovery from PCS-down/PMA-up bad states, ethtool module EEPROM reads, LED control behavior, and cleanup freeing `efx->phy_data`.
