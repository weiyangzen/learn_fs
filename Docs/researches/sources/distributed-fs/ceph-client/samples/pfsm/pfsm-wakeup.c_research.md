# sources/distributed-fs/ceph-client/samples/pfsm/pfsm-wakeup.c

Purpose: user-space power-fail safe mode wakeup sample coordinating RTC alarm and PFSM PMIC device wakeup setup.

Important APIs/functions: uses `/dev/rtc0`, PFSM device paths, `ioctl` on RTC/PFSM UAPI commands, `open`, `close`, time/alarm structures, and fixed `ALARM_DELTA_SEC`.

Control flow: opens RTC and PFSM PMIC devices, configures wakeup/alarm timing, arms PFSM-related wake behavior, and closes descriptors. It is a narrow platform demonstration for systems exposing the listed PMIC devices.

State and persistence: programs hardware/kernel device alarm state; no local files.

Dependencies and integration: RTC device, PFSM character devices, and platform PMIC topology.

Risks: hard-coded device nodes make it nonportable. Incorrect wake/alarm programming can affect platform power behavior.

Test signals: run on a supported PFSM platform, verify device opens/ioctls succeed, suspend/power event occurs, and wake happens around the configured alarm delta.
