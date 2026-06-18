# sources/distributed-fs/ceph-client/include/linux/power/sbs-battery.h

Purpose: defines platform data for SBS-compliant gas gauge battery drivers.

Important APIs and types: `struct sbs_platform_data` supplies I2C retry count and poll retry count after external change notifications.

Control flow: the SBS battery driver uses platform retry limits while reading gauge registers and while polling for new status after a notification.

State and persistence: static probe-time policy only; runtime battery data is in the driver/gauge.

Dependencies and integration points: integrates with power_supply and I2C/SMBus SBS gas-gauge handling.

Risks and test signals: risks include too few retries causing transient failures, too many retries delaying probe/status updates, and missing platform data. Test I2C error handling, external change notification polling, power_supply property reads, and timeout behavior.
