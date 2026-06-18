# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.h

## Purpose
This header defines the wil6210 platform abstraction. It lets the driver notify or request services from board/platform code and lets platform code call back into the driver for ramdump and firmware recovery.

## Important APIs, Types, and Functions
- `enum wil_platform_event` enumerates lifecycle notifications: firmware crash, pre-reset, firmware ready, pre-suspend, and post-suspend.
- `enum wil_platform_features` identifies platform-controlled features such as external firmware clock control and triple MSI.
- `enum wil_platform_capa` defines platform capabilities stored in `wil->platform_capa`, including radio-on suspend, T power-on 0, and external clock capability.
- `struct wil_platform_ops` contains platform callbacks for bus bandwidth requests, suspend/resume, uninitialization, event notification, capability retrieval, and feature setting.
- `struct wil_platform_rops` contains reverse callbacks from platform code into wil6210 for ramdump and firmware recovery.
- `wil_platform_init()`, `wil_platform_modinit()`, and `wil_platform_modexit()` are the public lifecycle APIs.

## Control Flow
The core driver initializes platform support by passing an ops table and optional reverse ops to `wil_platform_init()`. Platform code can fill ops and store reverse callbacks. Later driver lifecycle points can call `notify()`, `suspend()`, `resume()`, `bus_request()`, or feature/capability functions if present. Platform code can invoke `ramdump()` or `fw_recovery()` through the reverse ops when coordinating broader subsystem recovery.

## State and Persistence Behavior
The header defines callback contracts only. Runtime state lives in the platform implementation and in `wil6210_priv.platform_handle`, `platform_ops`, `platform_capa`, and `keep_radio_on_during_sleep`. Capabilities and features are in-memory policy state for the device lifetime.

## Dependencies and Integration Points
It forward-declares `struct device` and uses fixed-width integer and boolean types supplied by kernel includes in users. It integrates with PM, firmware recovery, crash dump, bus scaling, MSI setup, and clock/power policy in the main driver.

## Risks
Callback ownership and lifetime must be clear: the platform may copy reverse ops, and the returned handle must remain valid until uninit. Callers must check optional function pointers. Capability/feature enum ordering is part of the in-driver contract, so mismatches between platform code and driver can enable wrong power or interrupt behavior.

## Test Signals
Test with no platform implementation and with a populated platform implementation. Validate event ordering around firmware ready, crash, reset, suspend, and resume; bus bandwidth votes under traffic; capability bits reflected in driver policy; and ramdump/recovery callbacks during firmware crash handling.
