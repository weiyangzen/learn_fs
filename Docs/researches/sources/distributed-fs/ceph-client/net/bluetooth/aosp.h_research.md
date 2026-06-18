# sources/distributed-fs/ceph-client/net/bluetooth/aosp.h

## Purpose
This header provides the AOSP extension interface and no-op stubs when `CONFIG_BT_AOSPEXT` is disabled.

## Important APIs, Types, And Functions
It declares `aosp_do_open()`, `aosp_do_close()`, `aosp_has_quality_report()`, and `aosp_set_quality_report()` for enabled builds. Disabled builds inline no-op open/close, return `false` for quality-report support, and return `-EOPNOTSUPP` for quality-report configuration.

## Control Flow
There is no runtime control flow beyond inline stubs. The header lets core HCI code call AOSP hooks unconditionally without preprocessor branches at each call site.

## State, Persistence, And Dependencies
The functions operate on `struct hci_dev`. State is owned by HCI device fields and the implementation in `aosp.c`.

## Integration Points
HCI core and management code include this header to initialize and configure vendor extension behavior. The Makefile includes `aosp.o` only when `CONFIG_BT_AOSPEXT` is enabled.

## Risks
Callers must tolerate `-EOPNOTSUPP` in disabled builds. The header assumes `struct hci_dev` is visible from includers through surrounding HCI headers.

## Test Signals
Builds with and without `CONFIG_BT_AOSPEXT` should both compile, and disabled builds should expose no runtime BQR capability.
