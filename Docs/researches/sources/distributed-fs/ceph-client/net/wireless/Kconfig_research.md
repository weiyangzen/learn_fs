# sources/distributed-fs/ceph-client/net/wireless/Kconfig

## Purpose
This Kconfig file defines the wireless configuration feature set for cfg80211 and wireless extensions compatibility. It controls whether cfg80211 is built, how regulatory database verification works, whether debug/test/developer paths are included, and whether old WEXT interfaces are exposed.

## Important options
`CFG80211` is the primary tristate and selects firmware loading and CRC32, plus SHA256 when kernel regulatory DB keys are used. `NL80211_TESTMODE`, `CFG80211_DEVELOPER_WARNINGS`, and `CFG80211_KUNIT_TEST` enable test and developer-only paths. Regulatory options include `CFG80211_CERTIFICATION_ONUS`, `CFG80211_REQUIRE_SIGNED_REGDB`, `CFG80211_USE_KERNEL_REGDB_KEYS`, `CFG80211_EXTRA_REGDB_KEYDIR`, `CFG80211_REG_CELLULAR_HINTS`, and `CFG80211_REG_RELAX_NO_IR`. `CFG80211_DEBUGFS` gates debugfs files. `CFG80211_WEXT` selects WEXT compatibility. `CFG80211_DEFAULT_PS` enables default powersave.

## Control flow
Kconfig dependency flow places most options under `if CFG80211`. Certification-sensitive regulatory relaxations depend on `CFG80211_CERTIFICATION_ONUS`, and signature verification can select `SYSTEM_DATA_VERIFICATION`. WEXT support selects `WEXT_CORE`; proc and private WEXT helpers are controlled separately.

## State and persistence
This file does not store runtime state. It persists build-time configuration that determines compiled code paths and available kernel APIs.

## Dependencies and integration points
The options affect files in `net/wireless`, nl80211 userspace API availability, regulatory firmware loading, debugfs exposure, WEXT compatibility files, and test compilation.

## Risks
Regulatory options are high risk because enabling relaxations or disabling signature requirements can change compliance guarantees. Testmode should not be enabled in production kernels. WEXT compatibility increases legacy API surface.

## Test signals
Build matrix coverage should include cfg80211 built-in, module, disabled; signed regdb on/off; debugfs on/off; WEXT on/off; KUnit enabled; and certification-only regulatory relaxations.
