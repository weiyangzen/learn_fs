# sources/distributed-fs/ceph-client/drivers/platform/x86/winmate-fm07-keys.c

Purpose: polled input driver for five front-panel keys on Winmate FM07/FM07P systems. It reads an embedded-controller key byte through fixed I/O ports and reports keys as `KEY_F13` through `KEY_F17`.

Important APIs and control flow: module init DMI-gates on Winmate `IP30`, registers a platform driver, and creates a simple platform device. Probe allocates an input device, reserves command/data ports `0x6c` and `0x68`, enables EV_KEY bits, sets up polling with `fm07keys_poll()`, and registers the device. Polling flushes EC output, writes the read command and key address, waits for data ready, reads active-low bits, reports each key, and syncs.

State and dependencies: state is the platform device pointer and the input device managed by devres. It depends on DMI, legacy I/O port access, input polling, and platform device registration.

Risks and test signals: polling busy-waits up to `LOOP_TIMEOUT` without sleeps, so port behavior and timeout logging matter. Fixed ports can conflict with other EC users. Tests should confirm DMI gating, port reservation failure handling, 50 Hz polling behavior, active-low key mapping, timeout ratelimiting, and clean module unload.
