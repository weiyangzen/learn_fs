# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.c

Purpose: provides generic PHY register access wrappers and PHY Polling Unit coordination for mv88e6xxx internal PHYs.

Important APIs/types/functions: direct 6165 accessors call core `mv88e6xxx_read/write()`. Generic `mv88e6xxx_phy_read/write()` and C45 variants dispatch through chip ops and the default MDIO bus. Page helpers select a PHY page, read/write a register, and restore copper page. PPU helpers initialize/destroy mutex/timer/work state, disable PPU for direct register access, and re-enable it asynchronously.

Control flow: normal reads resolve the default MDIO bus and chip ops, returning `-EOPNOTSUPP` if absent. Paged reads/writes reject register 22 itself, switch page, perform access, and restore page. PPU-protected 6185 operations disable the PPU under `ppu_mutex`, perform raw access, then schedule re-enable after 10 ms via timer/work.

State and persistence: runtime state is `chip->ppu_mutex`, `ppu_timer`, `ppu_work`, and `ppu_disabled`. PHY register contents are hardware state; selected pages are restored to copper page after helper access.

Dependencies/integration: used by MDIO bus callbacks, PHY setup, and chip ops. Depends on module/MDIO APIs, timers/workqueues, and `phy.h` constants.

Risks: `mv88e6xxx_phy_page_write()` writes the page register twice before writing target register, which is redundant but benign if successful. PPU re-enable work uses `mutex_trylock`, so repeated contention can delay PPU restoration. Page restore errors are logged but cannot be recovered by caller.

Test signals: internal PHY C22/C45 reads through default MDIO bus, paged register access restoring copper page, PPU disable/re-enable around 6185 accesses, no-op PPU setup on chips without PPU ops, and teardown canceling timer/work.
