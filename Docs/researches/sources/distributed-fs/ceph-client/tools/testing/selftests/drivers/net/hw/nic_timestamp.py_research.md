
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nic_timestamp.py`

## Purpose
Tests hardware timestamping configuration paths on a real NIC, covering both the legacy `SIOCGHWTSTAMP` / `SIOCSHWTSTAMP` ioctl ABI and the ethtool netlink timestamp configuration API. It verifies that advertised TX timestamp types and RX filters can be applied and read back consistently through both interfaces.

## Important APIs, Types, And Functions
- `hwtstamp_config` and `ifreq` are `ctypes.Structure` mirrors of the kernel ABI structs needed by the ioctl path.
- `__get_hwtimestamp_support()` reads `EthtoolFamily.tsinfo_get()` and converts `tx-types` and `rx-filters` bitsets into testable lists.
- `__get_hwtimestamp_config_ioctl()` / `__set_hwtimestamp_config_ioctl()` wrap `fcntl.ioctl()` against `SIOCGHWTSTAMP` and `SIOCSHWTSTAMP`.
- `__get_hwtimestamp_config()` / `__set_hwtimestamp_config()` wrap `cfg.ethnl.tsconfig_get()` and `tsconfig_set()`.
- `__perform_hwtstamp_tx()` and `__perform_hwtstamp_rx()` implement the shared test loops used by `test_hwtstamp_*`.

## Control Flow
`main()` creates `NetDrvEnv(__file__, nsim_test=False)`, attaches an `EthtoolFamily`, and runs four ksft cases: TX via ioctl, TX via netlink, RX via ioctl, and RX via netlink. Each case saves the original timestamp configuration, iterates all supported advertised settings, applies one setting, reads it back through netlink and ioctl, asserts consistency, then restores the original configuration.

## State And Persistence
The file mutates NIC timestamp configuration. Restoration is explicit at the end of `__perform_hwtstamp_tx()` and `__perform_hwtstamp_rx()`, but not protected by `defer()` or `finally`, so a mid-loop assertion or unexpected exception can leave timestamp settings changed. Socket objects in ioctl helpers are closed after successful ioctl but not via a context manager.

## Dependencies And Integration Points
Depends on `lib.py` ksft helpers, `NetDrvEnv`, `EthtoolFamily`, and `NlError`. The test skips `EOPNOTSUPP` from netlink/ioctl as lack of hardware timestamping support. It is intended for hardware devices, not netdevsim.

## Risks
The code assigns `tscfg = orig_tscfg` and mutates nested fields, so the saved original dict can be altered before restoration unless the netlink family returns fresh immutable copies. RX tests allow drivers to broaden PTP filters by accepting returned RX filter indexes greater than requested, which is intentional but could hide overbroad behavior outside the PTP convention.

## Test Signals
Pass signals are ksft equality between netlink bit values and ioctl integer fields for all advertised TX/RX settings. Skip signals are `EOPNOTSUPP` for timestamp info/config support.
