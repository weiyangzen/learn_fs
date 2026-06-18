# sources/distributed-fs/ceph-client/drivers/net/phy/motorcomm.c

## Purpose
Implements Motorcomm YT8511, YT8521, YT8531, YT8531S, and YT8821 PHY support, including extended-register access, RGMII delay/drive strength, copper/fiber combo arbitration, WOL, LED hardware triggers, suspend/resume, autonegotiation, status decoding, and YT8821 2.5G tuning.

## Important APIs, Types, And Functions
`ytphy_read_ext()`, `ytphy_write_ext()`, and `ytphy_modify_ext()` implement page-select/data extended-register access. `struct yt8521_priv` stores combo advertising, polling mode, strap mode, and active page. YT8521/YT8531 use probe/config/status/aneg helpers; WOL uses `ytphy_set_wol()` or `yt8531_set_wol()`; LED support uses `yt8521_led_hw_control_*()`. YT8821 uses dedicated feature, init, status, rate-matching, suspend, and resume callbacks.

## Control Flow
YT8511 config programs RGMII delays and PLL sleep behavior. YT8521/YT8531 probes classify strap mode and configure clock output; config init applies RGMII delay, sleep/PLL policy, and drive strength. YT8521 combo mode saves advertising, configures UTP and fiber pages separately, then arbitrates active media on status reads with UTP priority. YT8821 init selects chip mode from interface, declares possible interfaces, initializes SerDes and UTP analog registers, disables auto sleep, and soft-resets.

## State And Persistence
Hardware registers hold most state. `yt8521_priv` persists combo media and advertising state across link changes. WOL stores MAC and enable bits in common extended registers. Device-tree properties influence clock output, sleep, PLL, delay, drive strength, and optional TX clock inversion.

## Dependencies And Integration Points
Depends on phylib, OF properties, ethtool WOL/LED helpers, genphy/C45 helpers, and MDIO page management. Registers five `phy_driver` entries and an MDIO ID table.

## Risks
Extended-register helpers require correct MDIO locking; LED callbacks use unlocked helpers and rely on external serialization. `yt8531_set_wol()` lacks the attached-device/MAC validation present in `ytphy_set_wol()`. Combo advertising is initialized once and may need scrutiny after later advertising changes. YT8821 live interface changes require MAC support. Long analog tuning sequences are revision-sensitive.

## Test Signals
Probe all IDs, test RGMII delay DT values, exercise YT8521 UTP/fiber switching, validate WOL wake, test LED trigger set/get, verify YT8531 drive-strength properties, and test YT8821 10/100/1000/2500 transitions with rate matching.
