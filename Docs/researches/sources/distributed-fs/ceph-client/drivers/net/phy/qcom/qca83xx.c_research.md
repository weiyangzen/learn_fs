# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qca83xx.c

Purpose: Implements internal PHY support for QCA8337 and QCA8327 switch PHY variants. It applies switch-revision-specific analog and EEE workarounds, exposes a small ethtool statistic set, manages suspend/resume quirks, and toggles a DAC amplitude adjustment for QCA8327 at 100 Mbps.

Important APIs and functions: `qca83xx_driver[]` registers entries for QCA8337, QCA8327-A, and QCA8327-B. Key functions are `qca83xx_probe()`, `qca83xx_config_init()`, `qca8327_config_init()`, `qca83xx_link_change_notify()`, `qca83xx_suspend()`, `qca8337_suspend()`, `qca8327_suspend()`, `qca83xx_resume()`, and ethtool stats helpers `qca83xx_get_sset_count()`, `qca83xx_get_strings()`, and `qca83xx_get_stats()`.

Control flow: Probe allocates per-PHY statistic storage. Config init reads switch revision from `phydev->dev_flags`, applies revision-specific debug/MMD writes, and sets gigabit prefer-master. QCA8327 init first disables manual DAC amplitude control, then runs the common init. Link-change notification enables +6 percent DAC amplitude only while QCA8327 is running at 100 Mbps and clears it otherwise. Suspend clears selected green/hibernation debug bits; QCA8337 also invokes generic suspend, while QCA8327 avoids full PHY power-down and instead modifies BMCR to avoid unreliable ports. Resume reinitializes config, resets and restarts autoneg, polls reset completion, and delays briefly.

State and persistence: Per-device state is an accumulated `u64 stats[]` array. Revision information is passed through `dev_flags`. Hardware tweaks live in debug registers, MMD registers, and BMCR and are re-applied on init/resume. No persistent storage is used.

Dependencies and integration: Depends on phylib, shared AT803x debug register helpers, ethtool stats callbacks, switch driver-provided revision flags, and internal PHY IDs associated with qca8k switch hardware.

Risks and test signals: Risks include revision flag mismatch, undocumented analog/debug values, stat counters accumulating incorrectly when reads fail, QCA8327 suspend unreliability, and link-change DAC tuning not being cleared. Test all three PHY IDs, switch revisions 1/2/4, suspend/resume cycles, 100M and 1G link transitions, ethtool stats reads including MMD errors, and prefer-master negotiation behavior.
