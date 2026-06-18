# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_mdio.c

## Purpose
`davinci_mdio.c` implements the DaVinci/CPSW MDIO bus driver. It supports normal hardware user-access transactions and a manual bitbang mode used on selected K3 SoCs, registers an `mii_bus`, integrates runtime PM/autosuspend, scans or registers DT-described PHYs, and handles system/runtime suspend.

## Important APIs, Types, and Functions
`struct davinci_mdio_regs` maps the MDIO register block, including control, alive/link status, user interrupt registers, manual interface, poll/manual mode, and user access/physel entries. `struct davinci_mdio_data` stores platform data, optional `mdiobb_ctrl`, registers, clock, device, bus, access timing, scan policy, divider, and manual-mode flag. Core functions include `davinci_mdio_init_clk()`, enable/disable/manual-mode helpers, `wait_for_user_access()`, `wait_for_idle()`, `davinci_mdio_read()`, `davinci_mdio_write()`, bitbang C22/C45 wrappers, reset helpers, probe/remove, and runtime/system PM callbacks.

## Control Flow and State
Probe allocates driver state and either a bitbang or normal MDIO bus, reads DT/platform bus frequency, chooses manual mode through SoC family matching, maps registers, computes the MDIO clock divider and conservative access time, enables runtime PM, optionally skips alive-register scan when DT child PHYs are present, and registers the bus with `of_mdiobus_register()`. Each hardware read/write resumes the device, waits for the user-access engine, issues a transaction, handles `-EAGAIN` when an idled controller must be re-enabled after EMAC reset interference, then autosuspends. Reset resumes the device, enables manual mode if needed, waits for scan logic to settle, logs version/frequency, and updates `phy_mask` from the alive register unless scan is skipped.

## Dependencies and Integration Points
This driver depends on PHYLIB, OF MDIO, `mdio-bitbang`, runtime PM, clocks, pinctrl sleep/default states, and SoC matching. DaVinci EMAC may locate this bus via `of_find_compatible_node()` when no PHY handle is provided.

## Risks and Test Signals
Clock-divider math assumes a valid input clock and nonzero bus frequency. Hardware access can time out or be reset mid-transaction by EMAC soft reset, so retry behavior and logs matter. Manual mode changes bus operations and uses bitbang C45 support, requiring coverage on AM62/AM64/AM65/J72 families. Test signals include bus registration with explicit DT PHY children and legacy scan-only DTs, alive mask correctness, runtime autosuspend around reads/writes, EMAC reset during MDIO access, C22/C45 bitbang transactions, suspend pinctrl state changes, and remove cleanup including `free_mdio_bitbang()`.
