<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c

Purpose: This file supports the EDOSK7760 board by declaring NOR flash, two SH7760 I2C controllers, SMC91x Ethernet, board setup, and the machine vector.

Important APIs/types/functions: It defines BSC register macros, flash partitions/data/resources/device, `sh7760_i2c_platdata`, I2C0/I2C1 resources/devices, SMC91x platform data/resources/device, `edosk7760_devices`, `init_edosk7760_devices`, and `mv_edosk7760`.

Control flow: The initcall configures/registers board platform devices. The board also programs bus-state-controller registers for external devices and supplies machine-vector callbacks.

State and persistence: Persistent state includes flash partition layout, I2C bus resources, Ethernet resource data, and machine-vector data.

Dependencies and integration points: It depends on SH7760 CPU support, physmap flash, SH7760 I2C driver, SMC91x driver, platform devices, and SuperH machine-vector infrastructure.

Risks and test signals: Bus timing registers and memory windows are board-specific and can break flash/Ethernet if wrong. Tests include flash partition detection, I2C adapter registration, Ethernet probe, and boot on EDOSK7760.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-edosk7760.c -->
