# sources/distributed-fs/ceph-client/drivers/hwmon/kfan.c

## Purpose
`kfan.c` is an auxiliary-bus hwmon driver for the KEBA fan controller FPGA IP core. It exposes fan fault and optionally fan RPM, plus writable PWM duty control.

## Important APIs, types, and functions
The driver uses auxiliary-bus matching, MMIO `ioread`/`iowrite`, dynamic `hwmon_channel_info`, and the hwmon `with_info` API. `struct kfan` stores the MMIO base, discovered tachometer/regulable capabilities, and per-instance channel config arrays. `kfan_get_fault()` interprets present/blocked status bits. `kfan_count_to_rpm()` converts tachometer counts to RPM. `kfan_set_pwm()` validates and writes duty values, forcing non-regulable controllers to on/off semantics.

## Control flow
Probe maps the KEBA fan resource, reads the status register, records whether tachometer and regulation are supported, builds fan and PWM channel descriptors accordingly, and registers a hwmon device named `kfan`. Runtime reads return fault, RPM, or PWM duty depending on sensor type. Writes are accepted only for `pwm1_input`.

## State and persistence
There is no software cache other than static capability flags read at probe. PWM writes change the hardware control register and persist until hardware reset or another agent writes it. Fault and RPM are read live.

## Dependencies and integration points
The driver depends on a KEBA parent auxiliary device named `keba.fan`, a valid MMIO resource, and a hardware register contract for status/control/tachometer values. It integrates with hwmon using per-instance dynamic channel descriptions.

## Risks
If the tachometer capability changes after probe, channel visibility will not update. Non-regulable fans accept any positive PWM request but coerce it to full on, which is sensible but may surprise userspace. RPM conversion assumes a fixed divider and count model. Fault reporting treats absent fans as faulted and blocked status as faulted only when no tachometer exists.

## Test signals
Test probe with all status bit combinations, channel visibility with/without tachometer, PWM writes at -1/0/1/255/256, non-regulable coercion, count conversion including 0 and 0xffff, and fault behavior for absent and blocked conditions.
