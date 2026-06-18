# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/phy.h

## Purpose
`phy.h` is a small Falcon PHY interface header that exposes operation tables and board-control helpers for supported external PHY families: 10Xpress/SFX7101, AMCC/Quake QT202x, and Transwitch CX4 retimer devices.

## Important APIs, Types, And Definitions
It declares `falcon_sfx7101_phy_ops`, `falcon_qt202x_phy_ops`, and `falcon_txc_phy_ops` as `struct ef4_phy_operations` instances. Helper declarations include `tenxpress_set_id_led()`, `falcon_qt202x_set_led()`, `falcon_txc_set_gpio_dir()`, and `falcon_txc_set_gpio_val()`. Quake LED constants describe LED modes (`QUAKE_LED_LINK_STAT`, `QUAKE_LED_LINK_ACT`, `QUAKE_LED_OFF`, `QUAKE_LED_ON`, and others) and whether a LED tracks TX or RX link. TXC GPIO direction constants distinguish input and output.

## Control Flow
This header contains declarations and constants only. Control flow is provided by PHY-specific implementation files and selected through `efx->phy_op` after hardware detection. Board or PHY code calls the LED/GPIO helpers to drive external status LEDs or retimer pins.

## State And Persistence
There is no local state. Persistent effects occur when implementations write PHY LED control registers, board GPIOs, or retimer state. The exported operation tables become persistent driver configuration once assigned to `efx->phy_op`.

## Dependencies And Integration Points
The header assumes `struct ef4_nic`, `enum ef4_led_mode`, and `struct ef4_phy_operations` are already visible through surrounding includes. It integrates the board layer, PHY probe logic, and generic link/ethtool code with concrete PHY implementations.

## Risks
Because constants map directly to hardware control states, wrong LED mode or GPIO direction values can misrepresent link status or affect board control pins. The header does not enforce include ordering by itself; users must include it in contexts where `net_driver.h` or equivalent definitions are present.

## Test Signals
Signals include successful PHY operation table selection, LED identify/default behavior, QT202x LED register writes, TXC GPIO direction/value behavior, and link-state reporting through the selected PHY implementation.
