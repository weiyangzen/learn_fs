# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-pmic-wrap.c

## Purpose
This driver implements the MediaTek PMIC wrapper bus controller. It initializes AP-side wrapper hardware and PMIC-side device-wrapper settings, exposes PMIC access through regmap, handles wrapper interrupts, supports multiple SoC/PMIC register layouts, and populates child devices under the PMIC node.

## Important APIs, Types, and Functions
Key types include `struct pmic_wrapper`, `struct pmic_wrapper_type`, `struct pwrap_slv_type`, and `struct pwrap_slv_regops`. Important functions include `pwrap_read16()`, `pwrap_read32()`, `pwrap_write16()`, `pwrap_write32()`, regmap callbacks, `pwrap_reset_spislave()`, `pwrap_init_sidly()`, `pwrap_init_dual_io()`, `pwrap_init_cipher()`, `pwrap_init_security()`, SoC-specific init helpers, `pwrap_init()`, `pwrap_interrupt()`, and `pwrap_probe()`.

## Control Flow and State
Probe matches the child PMIC node, allocates wrapper state, maps `pwrap` and optional bridge MMIO, obtains resets and clocks, enables DCM where supported, runs `pwrap_init()` unless `INIT_DONE2` indicates bootloader initialization, validates init-done status, configures watchdog/timer/interrupt masks, requests IRQ, registers regmap, and populates child devices. WACS read/write helpers poll FSM state, issue commands, wait for valid data, clear valid state, and recover stale `WFVLDCLR` state on timeout.

## Dependencies and Integration Points
The driver integrates with device tree master and slave compatibles, reset framework, clock framework, MMIO, IRQs, regmap, and OF platform population. PMIC child drivers access registers through the regmap backed by PMIC wrapper transactions. SoC descriptors define register offsets, arbiter masks, interrupt masks, SPI command format, watchdog masks, capabilities, and init callbacks.

## Risks and Test Signals
Risks are high because initialization ordering touches reset, SPI slave mode, SIDLY tuning, dual I/O, cipher/CRC security, arbiter enablement, watchdogs, and interrupts. Descriptor mistakes can break all PMIC communication; MT8195 has `NEED CONFIRM` comments for arbiter and interrupt masks. Test signals include PMIC regmap reads/writes, write-test values, SIDLY pass range, dual-IO read tests, cipher readiness, bootloader-initialized skip path, interrupt logs, child regulator/RTC/MFD probes, and suspend/resume PMIC access.
