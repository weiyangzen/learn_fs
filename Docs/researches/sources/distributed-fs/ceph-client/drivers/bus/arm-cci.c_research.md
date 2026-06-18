# sources/distributed-fs/ceph-client/drivers/bus/arm-cci.c

## Purpose
Provides ARM Cache Coherent Interconnect support, especially CCI-400 port control for low-level power management and platform population for CCI PMU child devices.

## Important APIs, Types, And Functions
Global initialization stores `cci_ctrl_base` and `cci_ctrl_phys`. Under `CONFIG_ARM_CCI400_PORT_CTRL`, `struct cci_ace_port` describes ACE/ACE-Lite ports, `struct cpu_port` caches logical CPU to CCI port mapping, and exported APIs include `cci_ace_get_port()`, `cci_disable_port_by_cpu()`, `__cci_control_port_by_device()`, `__cci_control_port_by_index()`, and `cci_probed()`. `cci_enable_port_for_self()` is naked ARM assembly for MMU-off cluster bring-up.

## Control Flow
`early_initcall(cci_init)` probes the first matching CCI node, maps the control block, parses child `arm,cci-400-ctrl-if` nodes, maps port registers, classifies ACE versus ACE-Lite ports, caches CPU MPIDR-to-port associations, and flushes cache lines so low-level noncoherent code can use the data. `core_initcall(cci_platform_init)` registers a platform driver whose probe only populates child devices once `cci_probed()` succeeds. Port control writes snoop/DVM enable bits and busy-waits on the CCI status register.

## State And Persistence
Runtime state is static and read-mostly after initialization: control MMIO address, port descriptors, port count, and CPU port cache. Hardware state is the port enable/disable state in CCI registers. There is no persistent software state.

## Dependencies And Integration Points
The driver depends on device tree matching for CCI-400/500/550, OF address parsing, platform population, ARM cache flush helpers, SMP MPIDR mapping, and optional PMU auxdata. It is called by low-level CPU/cluster power-management paths where normal locking may not be available.

## Risks And Test Signals
Risks are severe because port control runs in fragile power states: wrong MPIDR mapping, bad device-tree `interface-type`, missing cache maintenance, polling forever, or using general port control on CPU ACE ports. Test signals include early boot probe logs, CPU hotplug/idle cluster transitions, CCI PMU child device creation, and stress testing suspend/resume on CCI-400 platforms.
