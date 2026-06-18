# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed-test.c

Purpose: this KUnit companion file tests the ASPEED phase-to-tap conversion helper that is compiled from `sdhci-of-aspeed.c` when `CONFIG_MMC_SDHCI_OF_ASPEED_TEST` is enabled. It focuses on the arithmetic that maps requested phase degrees to ASPEED tap register values and the clock-inversion flag.

Important APIs, types, and functions: the tests call `aspeed_sdhci_phase_to_tap(NULL, rate, phase)` directly and compare against expected values with `KUNIT_EXPECT_EQ()`. `ASPEED_SDHCI_TAP_PARAM_INVERT_CLK` is included in expected outputs for phase requests at or above 180 degrees. The suite is named `sdhci-of-aspeed`.

Control flow: `aspeed_sdhci_phase_ddr52()` tests a 52 MHz DDR52-style rate around low-degree tap boundaries and around 180-degree inversion boundaries. `aspeed_sdhci_phase_hs200()` repeats equivalent boundary testing at 200 MHz, including maximum tap clamping near 90/270-degree requests. The `kunit_case` array registers both tests and `kunit_test_suite()` exposes the suite.

State and persistence: there is no persistent state. The test relies on a static helper included into the same translation unit as the production driver, so it can exercise a `static` function without exporting it.

Dependencies and integration points: this file depends on `<kunit/test.h>` and on being included from `sdhci-of-aspeed.c` after the helper and constants are defined. It is controlled by `CONFIG_MMC_SDHCI_OF_ASPEED_TEST`, not by runtime platform probing.

Risks: coverage is intentionally narrow: it verifies boundary arithmetic but not register writes, phase descriptor masks, DT phase parsing, or full clock programming. Passing `NULL` as device is safe for this helper because the device is only used for debug logging, but future helper changes could break that assumption.

Test signals: the direct signal is a passing KUnit suite named `sdhci-of-aspeed`. The selected values check off-by-one behavior, inversion at 180 degrees, and tap clamping for both 52 MHz and 200 MHz rates.
