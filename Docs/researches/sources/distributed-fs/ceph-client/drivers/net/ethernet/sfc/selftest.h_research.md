# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.h

## Purpose
Defines the top-level SFC self-test result ABI used inside the driver and declares the self-test and loopback callback APIs.

## Important APIs and types
`struct efx_loopback_self_tests` holds per-TX-queue sent/done counts plus aggregate good/bad RX counts. `struct efx_self_tests` contains online results (`phy_alive`, `nvram`, `interrupt`, per-channel event queue results) and offline results (`memory`, `registers`, PHY extended tests, loopback table). Declared functions are `efx_loopback_rx_packet()`, `efx_selftest()`, and async init/start/cancel helpers.

## Control flow and integration
Ettool allocates the result structure and passes it to `efx_selftest()`. RX delivery calls `efx_loopback_rx_packet()` while loopback testing is active. Driver init/open/stop/remove manage async delayed self-test work through the declared helpers.

## State and persistence behavior
All state is caller-owned in memory. Non-counter result fields use `1` for pass, `-1` for fail, and `0` for not run or unsupported.

## Dependencies
Depends on `net_driver.h` for NIC, channel, TX queue, and loopback constants. Array sizes depend on `EFX_MAX_CHANNELS`, `EFX_MAX_TXQ_PER_CHANNEL`, `EFX_MAX_PHY_TESTS`, and `LOOPBACK_TEST_MAX`.

## Risks
Changing result layout or dimensions without updating ethtool formatting breaks output alignment. Firmware reporting more than `EFX_MAX_PHY_TESTS` tests would exceed the fixed result array.

## Test signals
Compile-time users catch declaration drift. Runtime checks are ethtool self-test string/data count consistency and correct per-channel/per-loopback values.
