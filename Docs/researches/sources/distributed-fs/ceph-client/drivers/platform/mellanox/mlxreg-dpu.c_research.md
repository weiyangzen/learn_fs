# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxreg-dpu.c

## Purpose
Nvidia DPU platform driver that instantiates management subdevices for a BF3-based DPU reachable through an I2C CPLD/FPGA register map. It exposes register attributes through `mlxreg-io` and power/health events through `mlxreg-hotplug`.

## Important APIs, Types, And Functions
`struct mlxreg_dpu` stores platform data, copied hotplug data, and child platform devices. Static `mlxreg_core_data` arrays describe FPGA version/part-number fields, reset controls, boot progress, voltage regulator update status, UFM upgrade, power-good events, and health events. `mlxreg_dpu_regmap_conf` controls 16-bit register, 8-bit value access. `mlxreg_dpu_copy_hotplug_data()`, `mlxreg_dpu_config_init()`, and probe/remove manage lifecycle.

## Control Flow
Probe validates platform data, obtains the target I2C adapter, creates the DPU I2C client, initializes regmap, syncs cache, and reads `CONFIG3` to identify supported BF3 hardware. Configuration then registers `mlxreg-io` with the regmap and, when an IRQ is present, registers `mlxreg-hotplug` with copied hotplug tables and aggregation masks.

## State, Dependencies, Integration, Risks, Tests
State is represented by regmap cache, platform child-device handles, hotplug table copies, and the I2C client/adapter. Dependencies include `mlxreg` platform data, `mlxcpld` conventions, I2C, regmap, and child platform drivers. Integration points are DPU inventory/reset sysfs via `mlxreg-io` and power/health uevents via `mlxreg-hotplug`. Risks include unsupported DPU type rejection, stale static platform table mutation if not copied, missing IRQ skipping hotplug, regcache synchronization failures, and child registration cleanup ordering. Test signals include adapter deferral, `CONFIG3` BF3 detection, regmap readable/writeable filters, expected `mlxreg_io` attributes, hotplug event generation, and remove unregistering children and I2C references.
