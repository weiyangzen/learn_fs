# sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.h

Purpose: shared header for SCH56xx hwmon drivers. It declares virtual-register, regmap, and watchdog helper APIs implemented by `sch56xx-common.c`.

Important APIs/types/functions: declarations cover `devm_regmap_init_sch56xx()`, 16-bit regmap read/write helpers, raw virtual register read/write helpers, 16-bit and 12-bit latched reads, and `sch56xx_watchdog_register()`.

Control flow: SCH5627/SCH5636 include this header to access the common mailbox protocol and watchdog registration after the common module has created their platform devices.

State and persistence: the header defines no state, but its prototypes expose stateful operations over a shared EC mailbox that callers must serialize with their provided mutexes.

Dependencies/integration: includes Linux mutex and regmap declarations; relies on `struct device` declarations from included kernel headers.

Risks: callers must understand latch ordering for 12/16-bit reads and must pass the same lock used for hardware access. No inline documentation specifies error semantics beyond integer errno returns.

Test signals: compile coverage for SCH5627/SCH5636, symbol export/import resolution, and matching prototypes with implementation.
