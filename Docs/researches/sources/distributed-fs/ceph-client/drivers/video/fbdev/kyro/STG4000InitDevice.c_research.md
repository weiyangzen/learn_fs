
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000InitDevice.c

Purpose: low-level STG4000/Kyro initialization support. It programs SDRAM timings, computes PLL divider values, resets major hardware blocks, and sets the core clock through PCI configuration space.

Important APIs and functions: `InitSDRAMRegisters()` selects SDRAM arbiter/config/refresh values from subsystem id memory type and chip speed bits plus PCI revision. `ProgramClock()` searches PLL feedback/pre-divider/output-divider combinations for a requested clock within about 0.4 percent and returns the chosen clock plus F/R/P fields. `SetCoreClockPLL()` masks interrupts, disables core threads, resets register/TA blocks, initializes SDRAM, computes the 100 MHz core PLL, writes staged PLL mode words through PCI config register `0x70`, and finally asserts a broad software reset.

Control flow: `fbdev.c` calls `SetCoreClockPLL()` during probe and remove. The sequence depends on `pSTGReg` register macros and `pci_read/write_config_word()`. The PLL write sequence uses long busy-loop delays between config writes to satisfy hardware timing.

State and persistence: hardware state includes SDRAM controller registers, software reset bits, thread enables, interrupt mask, TA configuration, and PCI core PLL config. Static `CorePllControl` defines the PCI config offset.

Dependencies and integration: includes `STG4000Reg.h` for register layout/macros and `STG4000Interface.h` for exported declarations. Uses PCI subsystem id/revision to infer RAM properties.

Risks: delay loops are CPU-speed dependent and not sleepable. `ProgramClock()` assumes requested values in specific units and mutates output pointers only on success. Bad subsystem id returns `-EINVAL`, but caller currently does not strongly propagate/display all failure details. Reset sequencing is hardware-critical and can blank or destabilize the card.

Test signals: validate PLL output for known target clocks, subsystem id memory-type matrix, PCI config write ordering, failure on invalid memory/chip-speed indexes, and probe/remove behavior on real STG4000 hardware.
