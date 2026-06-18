# sources/distributed-fs/ceph-client/drivers/hwmon/raspberrypi-hwmon.c

Purpose: Raspberry Pi voltage alarm hwmon driver. It polls firmware throttling state, exposes undervoltage sticky alarm as `in0_lcrit_alarm`, logs state transitions, and notifies hwmon listeners.

Important APIs/types/functions: `struct rpi_hwmon_data` stores firmware handle, hwmon device, last throttled value, and delayed work. `rpi_firmware_get_throttled()` calls `RPI_FIRMWARE_GET_THROTTLED`, clears sticky bits via request value `0xffff`, compares undervoltage bit, logs, and emits `hwmon_notify_event()`.

Control flow: probe obtains parent firmware pointer, registers hwmon, initializes autocancel delayed work, and schedules polling every two seconds. Suspend cancels polling; resume immediately invokes the poll worker.

State and persistence: `last_throttled` stores the latest firmware status. Sticky bits are cleared as part of polling, so user-visible state is the last sampled alarm bit.

Dependencies/integration: Raspberry Pi firmware property interface, hwmon, delayed work, platform PM.

Risks: polling cadence can miss very short events except for firmware sticky behavior. Firmware errors are logged once and leave old state. Resume calls the worker directly, which also reschedules delayed work.

Test signals: undervoltage log transitions, `in0_lcrit_alarm`, hwmon uevents, suspend/resume polling, and firmware error handling.
