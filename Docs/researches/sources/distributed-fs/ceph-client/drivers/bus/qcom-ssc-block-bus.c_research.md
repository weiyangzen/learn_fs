# sources/distributed-fs/ceph-client/drivers/bus/qcom-ssc-block-bus.c

## Purpose
This driver sequences clocks, resets, power domains, halt registers, and MPM always-on clamp overrides required to access the Qualcomm SSC block over AHB, then populates child devices inside the block.

## Important APIs, Types, and Functions
`struct qcom_ssc_block_bus_data` stores register pointers, halt regmap, clocks, resets, power-domain devices, and AXI halt offset. `qcom_ssc_block_bus_init()` performs the enable/deassert/unhalt sequence. `qcom_ssc_block_bus_deinit()` reverses it. Helper groups attach, enable, disable, and detach named power domains `ssc_cx` and `ssc_mx`.

## Control Flow
Probe maps named MPM config registers, gets two resets and six clocks, parses `qcom,halt-regs` into a syscon regmap plus offset, attaches and votes power domains to `INT_MAX`, initializes the bus, and populates child nodes. Error paths unwind power-domain attach/enable for early failures, while `qcom_ssc_block_bus_init()` has detailed internal unwind for clock/reset sequencing failures. Remove deinitializes the block, disables/detaches power domains, and calls PM cleanup helpers.

## State and Persistence
Runtime state is device-private and devm allocated. Hardware state includes clamp override bits, reset assertions, AXI halt request, and enabled clocks. Power-domain performance votes persist while the device is bound.

## Dependencies and Integration Points
The driver depends on named resources, reset framework, CCF clocks, generic power domains, runtime PM, syscon/regmap, and OF population. It is an enablement wrapper for SSC child devices.

## Risks and Test Signals
Risks include `qcom_ssc_block_bus_init()` return value being ignored in probe, use of `clk_disable()` instead of `clk_disable_unprepare()` in unwind/deinit despite prepare-enable calls, and manual sequencing fragility. Test signals include successful child probing after power collapse, AXI halt acknowledgement/idle behavior, no clock/reset imbalance warnings, and correct cleanup on deferred probe or remove.
