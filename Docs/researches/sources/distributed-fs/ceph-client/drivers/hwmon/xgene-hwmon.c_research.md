# sources/distributed-fs/ceph-client/drivers/hwmon/xgene-hwmon.c

## Purpose
This platform hwmon driver exposes APM X-Gene SoC telemetry provided by the SLIMpro management processor or ACPI PCC. It reports SoC temperature, CPU power, IO power, and a temperature critical alarm notification.

## Important APIs, Types, And Functions
- `struct xgene_hwmon_dev` owns mailbox/PCC channels, mailbox client callbacks, synchronization primitives, async message FIFO, work item, hwmon device pointer, alarm state, and PCC latency.
- `xgene_hwmon_rd()` sends a synchronous SLIMpro mailbox command and waits for a response.
- `xgene_hwmon_pcc_rd()` performs the ACPI PCC shared-memory command flow, rings the mailbox doorbell, waits for completion, and copies response words back.
- `xgene_hwmon_reg_map_rd()` reads management-processor sensor registers and rejects invalid data.
- `xgene_hwmon_get_cpu_pwr()`, `xgene_hwmon_get_io_pwr()`, and `xgene_hwmon_get_temp()` compose sensor-specific values.
- `xgene_hwmon_rx_cb()` and `xgene_hwmon_pcc_rx_cb()` route synchronous responses versus async notifications.
- `xgene_hwmon_evt_work()` drains async messages and updates alarm state through `xgene_hwmon_tpc_alarm()`.

## Control Flow
Probe allocates context, initializes locks/completion/FIFO/work, configures the mailbox client, and selects OF mailbox mode when ACPI is disabled or PCC mode when ACPI is active. PCC probing reads the `pcc-channel` property, requests the PCC mailbox channel, verifies IRQ-based txdone support, and computes a timeout from PCC latency. The driver then registers a fixed hwmon group and schedules work in case messages arrived before registration completed.

Sysfs reads build a command message and synchronously query the remote processor. Power reads fetch whole-watt and milliwatt registers, combine to milliwatts, and report microwatts. Temperature reads sign-extend the raw register and report millidegrees Celsius. Async power-management messages are queued in a kfifo from callbacks and processed in workqueue context; TPC alarm messages update `temp_critical_alarm` and notify sysfs.

## State And Persistence
The driver stores only transient synchronization state and the latest critical alarm boolean. There is no telemetry cache; every input read performs a mailbox/PCC transaction. Async messages persist only until drained from the fixed-size FIFO. PCC command state lives in ACPI shared memory during each transaction.

## Dependencies And Integration Points
It integrates with platform devices, OF compatible `apm,xgene-slimpro-hwmon`, ACPI IDs `APMC0D29`/`APMC0D8A`, ACPI PCC, mailbox framework, kfifo, workqueues, hwmon sysfs groups, and sysfs notification. It uses endianness-safe PCC shared-memory accesses and mailbox callbacks for both synchronous and asynchronous data.

## Risks
- The async FIFO is fixed at 16 messages and `kfifo_in_spinlocked()` return values are not checked, so notifications can be dropped under burst load.
- Synchronous request matching accepts several message shapes; unexpected remote firmware behavior could complete the wrong waiter.
- PCC timeout is an arbitrary multiplier of nominal latency, so slow firmware can produce false timeouts.
- `xgene_hwmon_rx_ready()` checks readiness with `IS_ERR_OR_NULL(ctx->hwmon_dev)` and `!resp_pending`; early async messages are queued, but lifecycle races around remove rely on callback quiescing from mailbox teardown.
- No telemetry cache means sysfs polling can stress firmware/mailbox paths.

## Test Signals
Validate both OF SLIMpro and ACPI PCC probe paths, missing `pcc-channel`, mailbox request failures, PCC without IRQ txdone, timeout/error responses, invalid sensor data bit handling, signed negative temperature conversion, power unit conversion, async TPC alarm notification and sysfs_notify, FIFO overflow behavior, and remove ordering with pending work/callbacks.
