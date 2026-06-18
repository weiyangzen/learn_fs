<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c

Purpose: implements the STM32 voltage-reference buffer regulator. It exposes selectable VREF output voltages, manages the VREFBUF clock with runtime PM, and waits for hardware readiness when enabling.

Important APIs/types/functions: `struct stm32_vrefbuf` stores MMIO base, clock, and device. `stm32_vrefbuf_enable()` resumes runtime PM, clears high impedance, sets enable, and polls `STM32_VRR`. `stm32_vrefbuf_disable()` clears enable. `stm32_vrefbuf_set_voltage_sel()` and `stm32_vrefbuf_get_voltage_sel()` manipulate the `STM32_VRS` field. Runtime PM callbacks prepare/disable the clock. The descriptor `stm32_vrefbuf_regu` exposes four table voltages: 2.5 V, 2.048 V, 1.8 V, and 1.5 V.

Control flow: probe allocates private state, maps MMIO, obtains the clock, sets up runtime PM autosuspend, enables the clock, registers the regulator with OF init data, stores the regulator device as platform data, and drops the runtime PM reference. Runtime operations resume the device for register access and autosuspend afterward. Remove unregisters the regulator, disables the clock, and shuts down runtime PM.

State and persistence: private state tracks clock/MMIO handles. Hardware CSR bits store enable, high-Z, readiness, and voltage selection. Runtime PM state controls the clock and is rebuilt on probe.

Dependencies and integration: depends on platform MMIO, `st,stm32-vrefbuf` OF node, a clock, `vdda` supply, runtime PM, and regulator consumers such as ADC/DAC reference users.

Risks and test signals: probe uses non-devm `regulator_register()`, making remove cleanup mandatory. Enable failure attempts to restore disabled/high-Z state. Runtime suspend/resume uses the regulator device from driver data, so ordering around remove should be tested. Test voltage selector get/set, enable timeout and rollback, autosuspend clock transitions, system sleep PM force suspend/resume, missing clock/resource errors, and regulator unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-vrefbuf.c -->
