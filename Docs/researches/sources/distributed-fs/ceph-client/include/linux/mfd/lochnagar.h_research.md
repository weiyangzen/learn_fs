# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar.h

Purpose: This header defines the shared Cirrus Logic Lochnagar audio board MFD core data and common base registers. It supports Lochnagar1 and Lochnagar2 devices and provides the analogue configuration update entry point.

Important APIs, types, and functions: `enum lochnagar_type` distinguishes `LOCHNAGAR1` and `LOCHNAGAR2`. `struct lochnagar` stores the board type, parent device, regmap, and `analogue_config_lock`. Common register macros cover software reset and firmware ID registers plus device and revision ID masks/shifts. `lochnagar_update_config` is exported to apply pending analogue configuration updates.

Control flow, state, and persistence: Consumers update regmap fields for clocks, audio routing, GPIOs, regulators, or analogue paths, then call `lochnagar_update_config` for hardware that latches analogue changes. The mutex protects updates while hardware processes the previous analogue update. Persistent state is board register configuration and firmware identity.

Dependencies and integration points: It depends on device, mutex, and regmap infrastructure. It integrates with `lochnagar1_regs.h`, `lochnagar2_regs.h`, audio clock/routing drivers, regulators, GPIO, and board MFD child devices.

Risks and test signals: Risks include missing the analogue update/latch step, failing to hold the lock around related analogue changes, and using Lochnagar1 register definitions on Lochnagar2. Test signals include device/revision ID reads, concurrent analogue update tests, audio route changes, regulator/GPIO child probes, and reset recovery.
