# sources/distributed-fs/ceph-client/drivers/watchdog/ib700wdt.c

## Purpose
`ib700wdt.c` is a legacy miscdevice watchdog for IB700 single-board computers. It controls the watchdog with fixed I/O ports for start/ping and stop and exposes the classic `/dev/watchdog` ABI.

## Important APIs, types, and functions
Global state includes platform device pointer, open bit, spinlock, timeout, nowayout, and magic-close marker. Hardware helpers are `ibwdt_ping`, `ibwdt_disable`, and `ibwdt_set_heartbeat`. File operations are `ibwdt_write`, `ibwdt_ioctl`, `ibwdt_open`, and `ibwdt_close`; platform lifecycle uses self-registered platform device and probe/remove/shutdown callbacks.

## Control Flow
Module init creates a platform device and probes the driver. Probe reserves `WDT_STOP` and `WDT_START` I/O ports, validates timeout, and registers `/dev/watchdog`. Open enforces single-open, pins module when nowayout, and activates the watchdog. Ping encodes timeout into the board's 0-F level value and writes `WDT_START`. Stop writes `WDT_STOP`. Release disables only after magic close; otherwise it pings and leaves hardware running.

## State and Persistence
State is global and not watchdog-core based. Hardware state persists in the board watchdog until stopped or reset. Shutdown disables the watchdog for soft shutdown.

## Dependencies and Integration Points
The driver depends on raw I/O ports `0x441` and `0x443`, platform-device self-registration, miscdevice watchdog ABI, compat ioctl handling, and module parameters.

## Risks and Test Signals
Risks include lack of hardware discovery, timeout tolerance/encoding, single-open global state, magic-close handling, and I/O port conflicts. Tests should cover timeout range 0-30, start/stop port writes, unexpected close, nowayout module ref, shutdown disable, and request_region failure.
