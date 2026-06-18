# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet_wol.c

## Purpose

`bcmgenet_wol.c` implements Wake-on-LAN support for Broadcom GENET. It bridges ethtool WOL configuration, optional PHY WOL support, MAC Magic Packet Detection, secure magic password programming, ACPI/filter wake mode, wake IRQ enablement, and the power-down/power-up transitions used by `bcmgenet.c` suspend and resume paths.

## Important APIs and Functions

The public internal APIs are `bcmgenet_get_wol`, `bcmgenet_set_wol`, `bcmgenet_wol_power_down_cfg`, and `bcmgenet_wol_power_up_cfg`. `bcmgenet_get_wol` first asks the PHY for its WOL settings, then overlays MAC wake capabilities when the platform device is wake-capable: `WAKE_MAGIC`, `WAKE_MAGICSECURE`, and `WAKE_FILTER`. It reports PHY secure-password data when PHY WOL owns it, otherwise reports the MAC password from `priv->sopass`.

`bcmgenet_set_wol` tries `phy_ethtool_set_wol` first. If the PHY handles a nonzero WOL request, that result is returned. Otherwise it validates MAC-supported options, stores `WAKE_MAGICSECURE` password bytes, toggles `device_set_wakeup_enable`, and balances `enable_irq_wake`/`disable_irq_wake` for the dedicated WOL IRQ and `irq0` through `priv->wol_irq_disabled`.

Private helpers are `bcmgenet_poll_wol_status`, which waits up to roughly 50 ms for `RBUF_STATUS_WOL`, and `bcmgenet_set_mpd_password`, which writes the 6-byte secure-on password into the UniMAC MPD password registers.

## Control Flow

During suspend with MAC WOL enabled, `bcmgenet_wol_power_down_cfg` only accepts `GENET_POWER_WOL_MAGIC`. It enables MPD when magic packet options are set, programs the secure password when requested, enables HFB ACPI mode, waits for WOL-ready status, forces the PHY state to `PHY_READY` to suppress normal link updates, enables the WOL clock, enables CRC forwarding and RX in `UMAC_CMD`, clears software reset if necessary, and unmasks MPD/HFB wake interrupts.

During resume, `bcmgenet_wol_power_up_cfg` disables the WOL clock, clears the cached CRC-forward flag, masks wake interrupts, unmasks MDIO interrupts when supported, disables MPD and ACPI mode, clears CRC forwarding in UniMAC, and restores the PHY state to `PHY_RUNNING` or `PHY_NOLINK` based on current link. It returns `-EPERM` when it detects the MAC was already reset enough that MPD or ACPI bits are gone; the caller uses this as a signal to continue through a fuller reset path.

## State and Persistence Behavior

WOL state is stored in `struct bcmgenet_priv`: `wolopts`, `sopass`, `clk_wol`, `wol_irq`, `irq0`, `wol_irq_disabled`, and `crc_fwd_en`. The driver also changes device wakeup state in the platform device and wake state in IRQ core. Hardware state includes MPD control/password registers, HFB ACPI enable, RBUF WOL status, interrupt masks, and UniMAC RX/CRC-forward bits. There is no persistent storage; ethtool settings live in memory for the netdev/device lifetime.

## Dependencies and Integration Points

This file depends on phylib WOL operations, ethtool WOL flags, platform PM wake APIs, IRQ wake APIs, clocks, UniMAC registers from `unimac.h`, and shared GENET definitions from `bcmgenet.h`. `bcmgenet.c` calls the power transition functions from its suspend/resume noirq flow and exposes get/set WOL through ethtool ops. The code assumes `dev->phydev` is present during WOL power transitions and directly modifies PHY state under the PHY lock.

## Risks and Edge Cases

Wake IRQ balancing is delicate: `priv->wol_irq_disabled` prevents unbalanced wake enable/disable calls, but wrong initialization or partial request failure could leave wake state inconsistent. MAC and PHY WOL capabilities are merged, and PHY WOL takes precedence for supported nonzero options, so testing must cover mixed PHY/MAC support. The power-down path rolls back MPD and HFB ACPI bits if WOL-ready polling times out. CRC forwarding is deliberately enabled during WOL so received wake frames include FCS handling expectations; resume must clear it. The `-EPERM` resume cases are not generic permission failures; they signal that hardware was already reset and that the main driver should take the full reinitialization path.

## Test Signals

Useful signals include `ethtool -s wol g` and secure magic password programming, PHY-only WOL versus MAC WOL behavior, disabling WOL after enabling it and checking wake IRQ balance, suspend/resume with magic packet wake, WAKE_FILTER/HFB wake rules from `bcmgenet.c`, polling timeout behavior, and resume after firmware or hardware reset where MPD/ACPI bits are already cleared. Runtime diagnostics include "polling wol mode timeout" and invalid/unsupported mode errors.
