# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.h

Purpose: declares IPA power management APIs and exposes `ipa_pm_ops` to the platform driver.

Important APIs: `ipa_core_clock_rate()` is used by endpoint HOL timer encoding on pre-Qtime IPA versions. `ipa_power_retention()` controls optional register retention across power collapse. `ipa_power_init()` and `ipa_power_exit()` own clock, interconnect, QMP, and runtime PM lifecycle. `ipa_pm_ops` supplies suspend/resume/runtime callbacks.

Control flow: main probe initializes power before allocating the full IPA structure because config needs clocks/interconnects ready. Main driver registers `ipa_pm_ops`; endpoint/main code uses runtime PM references around register and channel work.

State/persistence: the `struct ipa_power` type is opaque; persistence is managed in `ipa_power.c`.

Dependencies/integration: forward-declares `struct device`, `struct ipa`, and `struct ipa_power_data` from configuration tables.

Risks: consumers should not assume power is enabled merely because `ipa_power_init()` succeeded; register access still requires runtime PM active.

Test signals: platform driver binds with PM ops, runtime PM references allow register access, and endpoint timer calculations see the configured core rate.
