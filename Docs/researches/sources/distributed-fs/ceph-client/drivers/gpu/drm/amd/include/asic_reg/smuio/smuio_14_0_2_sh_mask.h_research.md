# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_sh_mask.h

## Purpose

`smuio_14_0_2_sh_mask.h` is a generated AMDGPU SMUIO 14.0.2 register bitfield header. It exports C preprocessor constants for field shifts and masks in SMUIO MMIO registers; it does not define functions, structs, storage, or executable logic. The companion offset header supplies register addresses, while this file supplies the field layout used by `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` users.

The covered address blocks are `smuio_smuio_tsc_SmuSmuioDec`, `smuio_smuio_swtimer_SmuSmuioDec`, `smuio_smuio_misc_SmuSmuioDec`, `smuio_smuio_i2c_SmuSmuioDec`, `smuio_smuio_rom_SmuSmuioDec`, and `smuio_smuio_gpio_SmuSmuioDec`. In the local tree, `amdgpu/smuio_v14_0_2.c` includes this header and uses the matching offsets for the ROM index/data registers and the golden TSC counter. The I2C macro families match the DesignWare-style SMU I2C programming model used by `amdgpu/smu_v11_0_i2c.c` on earlier SMUIO generations.

## Important APIs, types, and macro families

The public surface is entirely macro based. Each implemented field uses the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention. Registers with full-width payloads, such as scratch registers, ROM data words, and SMIO control words, typically have a shift of zero and a full-width or nearly full-width mask.

The TSC block defines fields for power-good reference-clock gap programming, golden TSC increment/count upper and lower halves, SOC golden TSC shadow halves, and `SOC_GAP_PWROK`. `GOLDEN_TSC_COUNT_UPPER` is a 24-bit high word and `GOLDEN_TSC_COUNT_LOWER` is a 32-bit low word, which explains the consumer pattern in `smuio_v14_0_2_get_gpu_clock_counter()`: read high, read low, reread high, and reread low if the high word changed.

The software timer block defines `PWR_VIRT_RESET_REQ` for VF/PF FLR request bits, display timer control/debug pairs for timer 1 and timer 2, global pulse width/enable, and interrupt-handler credit/trigger/clock-gate control in `PWR_IH_CONTROL`. These definitions are register-level ABI for reset request propagation and power/display timer interrupts.

The misc block defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, and eight scratch registers. `SMUIO_MCM_CONFIG` exposes die, package, socket, package subtype, console, and die-configuration fields. These fields are commonly consumed by ASIC-specific SMUIO callbacks to derive package topology, die identity, and socket identity.

The I2C block is the largest non-ROM section. It defines two nearly parallel controllers: `CKSVII2C_*` and `CKSVII2C1_*`. Each controller has configuration, target/slave/high-speed address, data command, SCL timing, interrupt status/mask/raw status, FIFO thresholds and levels, clear-on-read interrupt clear registers, enable/abort/status, SDA hold/setup, general-call acknowledgement, enable status, spike length, component parameter/version/type, and clock-gating support through `SMUIO_PWRMGT`. Field names map closely to a Synopsys DesignWare APB I2C register interface: `IC_MASTER_MODE`, `IC_MAX_SPEED_MODE`, `IC_RESTART_EN`, `DAT`, `CMD`, `STOP`, `RESTART`, `R_TX_ABRT`, `TFNF`, `TFE`, `RFNE`, `ENABLE`, `ABORT`, and `IC_EN`.

The ROM block defines SPI/ROM access control fields in `ROM_CNTL`, page mirroring in `PAGE_MIRROR_CNTL`, busy/done status registers, clock-gating delay and override fields in `CGTT_ROM_CLK_CTRL0`, index/data/start registers, software command sizing and return-data enable, a packed instruction/address command register, and a 64-word `ROM_SW_DATA_*` payload window. `smuio_v14_0_2.c` exposes `regROM_INDEX` and `regROM_DATA` through `amdgpu_smuio_funcs` for higher-level ROM access.

The GPIO block defines pad mask, output/input/enable/receiver/pull-up/pull-down/pinstrap state, GPIO interrupt status/enable/type/polarity/acknowledge registers, PCC and per-interrupt select registers, multi-processor interrupt status registers, SMIO index, S0/S1 VID SMIO values, open-drain selection, and SMIO enable state. Most GPIO vectors use 31-bit masks, reserving bit 31 or using bit 31 for software-initiated interrupt state depending on the register.

## Control flow

There is no runtime control flow in this header. Control flow appears in consumers after macro expansion. The most direct local path is `smuio_v14_0_2_get_gpu_clock_counter()`, where the TSC register offsets and masks support a stable 64-bit counter read with preemption disabled. ROM callbacks use offset macros to return addressable ROM index/data MMIO locations. I2C consumers use this style of mask header to compose command words, poll FIFO/status fields, detect abort causes, and clear sticky interrupt/status state.

## State and persistence behavior

The state described here is hardware state, not software-owned memory. TSC count and shadow registers represent live clock-counter state. `SMUIO_MCM_CONFIG`, pinstrap, DFT pinstrap, and IP discovery registers are platform identity/configuration state. Scratch registers persist as SMUIO MMIO scratch words until overwritten or reset. I2C enable, abort, FIFO, interrupt, clear, timing, and abort-source fields describe live controller state and sticky status. ROM index, data, software command, busy, and done fields describe SPI ROM transactions. GPIO pad configuration, interrupt enables, ack bits, and open-drain/SMIO settings persist in hardware until reset or driver/firmware reprogramming.

Many fields are command-like or clear-on-read/write-one-to-clear by hardware convention, especially I2C clear registers, GPIO interrupt acknowledge fields, ROM software command/done state, timer interrupt acknowledge fields, and FLR request bits. The header encodes bit positions only; ordering, timeout, locking, and clear semantics must come from the SMUIO hardware specification and driver call sites.

## Dependencies and integration points

This header must be used with the matching SMUIO 14.0.2 offset/default register set. Mixing it with another ASIC generation risks decoding the right register name with the wrong field layout. It depends on AMDGPU's generated register convention and Linux kernel C preprocessor compilation.

Integration points include `amdgpu_smuio_funcs` callbacks for ROM offsets and GPU clock counter reads, SOC15 MMIO helper code, SMU I2C transfer paths, VBIOS/SPI ROM access paths, GPU reset/FLR paths, GPIO/pinstrap discovery, platform topology detection, and power/display timer interrupt handling. The I2C fields also integrate indirectly with Linux I2C adapter behavior through SMU-managed buses used for board management devices.

## Risks

The main risk is silent bitfield drift. A wrong shift or mask can return an incorrect die/socket/package value, corrupt a 64-bit TSC read, write a reserved I2C or GPIO bit, mis-handle an FLR request, or program ROM/SPI timing incorrectly. The repeated CKSVII2C and CKSVII2C1 blocks are especially copy-error-prone because most fields are identical except for controller suffixes and some field names.

Partial mask coverage is another risk: several I2C registers are named but have sparse or no masks in this file, so consumers that assume every field has a mask may fail to compile or fall back to raw constants. ROM software data registers are numerous and repetitive, making off-by-one generation errors visible only when large ROM command payloads are exercised. GPIO interrupt vectors reserve or special-case high bits; treating every register as a full 32-bit GPIO vector can acknowledge or enable software-initiated interrupts unexpectedly.

## Test signals

Useful validation includes building AMDGPU with SMUIO 14.0.2 support enabled, compiling all consumers that include the matching offset and mask headers, and booting hardware that uses `smuio_v14_0_2_funcs`. Runtime signals include stable monotonic GPU clock counter reads across high-word rollover, successful VBIOS ROM index/data access, correct I2C transfers with STOP/RESTART and abort detection, GPIO interrupt and pinstrap reads matching board design, and no reserved-bit warnings or register access faults under MMIO tracing.

Hardware tests should cover reset/FLR request handling, display/power timer interrupt status and acknowledge paths if used, ROM busy/done polling, clock-gating state around ROM and I2C blocks, and I2C timeout/NAK recovery. Regression tests should compare generated macro names and field values against the authoritative ASIC register database, because ordinary unit tests will not catch many semantic mask mistakes.
