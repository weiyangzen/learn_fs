# sources/distributed-fs/ceph-client/include/linux/framer/framer.h

## Purpose
This header defines the consumer-facing generic framer API for telecom line framers, including configuration, status, power/runtime PM, notifier registration, and device lookup.

## APIs, types, and control flow
Enums describe E1/T1 interfaces and external/internal clocks. `struct framer_config` carries interface, clock type, and line clock rate. `struct framer_status` reports link state, and `FRAMER_EVENT_STATUS` identifies status notifications. `struct framer` embeds a device, id, ops pointer, mutex, init/power reference counts, regulator, work for notifications, blocking notifier list, delayed polling work, and previous status. Consumer calls get a framer, initialize it, power it on, set/get config, read status, register notifiers, then power off/exit and put. With `CONFIG_GENERIC_FRAMER` disabled, operations return `-ENOSYS`, get returns `ERR_PTR(-ENOSYS)`, and optional devm get returns `NULL`.

## State and dependencies
State is shared by multiple consumers through init and power refcounts protected by the framer mutex. Dependencies include device core, OF, mutexes, regulators, workqueues, and blocking notifiers.

## Integration, risks, and tests
Line interface consumers, network/HDLC drivers, and provider drivers use this API. Risks include unbalanced init/power counts, notifier callbacks after put, optional-get handling, PM runtime mismatch, and config/status calls before init. Tests should cover refcounted init/power sequencing, optional absent framer, notifier registration/unregistration, polling status changes, runtime PM errors, and disabled stubs.
