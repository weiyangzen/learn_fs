<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c

Purpose: registers fixed-voltage STM32MP PWR internal regulators for 1.1 V, 1.8 V, and USB 3.3 V rails using memory-mapped PWR control bits.

Important APIs/types/functions: `struct stm32_pwr_reg` stores the mapped base address and ready bit. `stm32_pwr_reg_enable()` sets a regulator enable bit in `REG_PWR_CR3` and polls the matching ready bit. `stm32_pwr_reg_disable()` clears the enable bit and polls until disabled. `stm32_pwr_reg_is_enabled()` and `stm32_pwr_reg_is_ready()` read the same register. `stm32_pwr_desc[]` defines the three fixed regulators and supplies.

Control flow: probe maps the MMIO resource, then allocates one small private object per regulator with the common base and a per-regulator ready mask. Each descriptor is registered with its private data. Enable writes the bit and polls up to 20 ms; disable clears the bit and polls up to 20 ms.

State and persistence: private state only points at MMIO and records the ready mask. Hardware register bits hold enable/ready state. There is no suspend/resume or software persistence.

Dependencies and integration: depends on platform MMIO resources, OF compatibles `st,stm32mp1,pwr-reg` and `st,stm32mp13-pwr-reg`, regulator core, and consumers of `reg11`, `reg18`, and `usb33`.

Risks and test signals: direct read-modify-write on `REG_PWR_CR3` has no explicit locking, so concurrent regulator operations could race if the regulator core does not serialize them. Timeout values are arbitrary. Test MMIO mapping failure, each rail enable/disable timeout path, ready bit polarity, fixed voltage reporting, and simultaneous operations on different rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stm32-pwr.c -->
