# sources/distributed-fs/ceph-client/drivers/net/dsa/Kconfig

Purpose: top-level Kconfig menu for DSA switch drivers, gated by `NET_DSA`. It sources vendor submenus and declares tristate symbols for DSA switch families and frontends.

Important APIs/types/functions: Kconfig symbols include `NET_DSA_BCM_SF2`, `NET_DSA_LOOP`, `NET_DSA_MT7530*`, `NET_DSA_MV88E6060`, `NET_DSA_RZN1_A5PSW`, `NET_DSA_KS8995`, `NET_DSA_SMSC_LAN9303*`, `NET_DSA_VITESSE_VSC73XX*`, and `NET_DSA_YT921X`. It sources b53 and other vendor Kconfig files.

Control flow: Kconfig enters the menu only when `NET_DSA` is enabled. Symbols select or imply DSA tag protocols, PHY/PCS helpers, regmap helpers, and transport frontends. B53 is integrated by `source "drivers/net/dsa/b53/Kconfig"`.

State and persistence behavior: Build-time configuration only; selected symbols persist in `.config` and drive which objects/modules Kbuild emits.

Dependencies and integration points: Integrates DSA core, tag protocols, SPI/I2C/MMIO dependencies, architecture predicates, PHY/PCS helpers, and vendor submenus.

Risks: `select` can bypass selected-symbol dependencies; Kconfig/Makefile mismatches can produce missing objects; architecture defaults can unexpectedly enable code; missing sourced files break config parsing.

Test signals: `olddefconfig/menuconfig`, allmodconfig/allnoconfig builds, per-symbol module/built-in builds, and Makefile symbol cross-checks.
