# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_offset.h

## Purpose

`smuio_15_0_8_offset.h` is the generated SMUIO 15.0.8 offset map. It defines register offsets and base indices for TSC, software timer, misc, I2C, ROM, and GPIO address blocks. It contains no executable C logic; consumers pass its `reg...` constants to AMDGPU SOC15 register access helpers and pair them with the matching `smuio_15_0_8_sh_mask.h` bitfield header.

The local integration point is `amdgpu/smuio_v15_0_8.c`, which includes this file and uses offsets for golden TSC reads, ROM index/data callbacks, ROM clock-gating state, `SMUIO_MCM_CONFIG` platform topology/package callbacks, and APU/non-APU gating around ROM clock control.

## Important APIs, types, and macros

The public API is a list of `regREGISTER` and `regREGISTER_BASE_IDX` macros. The TSC block at base address comment `0x5a8a0` defines PWROK gap, golden TSC increment/count, SOC golden TSC shadow, and SOC power-good gap registers. These support the high-low-high counter-read sequence used by `smuio_v15_0_8_get_gpu_clock_counter()`.

The software timer block at base address comment `0x5aca8` defines `PWR_VIRT_RESET_REQ`, display timer 1 and 2 control/debug registers, global control, and `PWR_IH_CONTROL`. Unlike 15.0.0, this offset map does not include display timer elapsed-control registers, so timer 2 starts at `0x012d` and the global/IH registers follow at `0x012f` and `0x0130`.

The misc block at base address comment `0x5a000` defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, and scratch registers 0 through 7. The scratch offsets are shifted relative to 15.0.0, running from `0x01c9` through `0x01d0`, and this file does not define `IO_SMUIO_PINSTRAP`. `smuio_v15_0_8.c` reads `regSMUIO_MCM_CONFIG` for die ID, socket ID, topology ID, package type, XGMI host-GPU support, and disabled-out Ethernet/custom-HBM probes.

The I2C block at base address comment `0x5a100` defines two CKSVII2C controller register windows. Controller 0 runs from `regCKSVII2C_IC_CON` at `0x0040` through component type at `0x006f`, with gaps for reserved/unimplemented addresses. Controller 1 mirrors the same register set from `0x0080` through `0x00af`, using `CKSVII2C1_*` names. The block also defines `regSMUIO_PWRMGT` at `0x018c` for I2C clock gating.

The ROM block at base address comment `0x5a380` defines ROM control/status/index/data/start/software-command registers and a 64-word `ROM_SW_DATA_1` through `ROM_SW_DATA_64` payload window from offsets `0x00ec` through `0x012b`. `smuio_v15_0_8_get_rom_index_offset()` and `get_rom_data_offset()` expose the index/data offsets, and `get_clock_gating_state()` reads `regCGTT_ROM_CLK_CTRL0` on non-APU devices.

The GPIO block at base address comment `0x5a500` defines software interrupt status, GPIO pad mask/output/impedance/enable/input/receiver/pull configuration, pinstraps, DFT pinstraps, interrupt status/ack/enable/type/polarity, PCC selection, S0/S1/SCHMEN/SCL/SDA controls, four interrupt select registers, four MP interrupt status registers, SMIO index, S0/S1 VID SMIO controls, open-drain selection, and `SMIO_ENABLE`.

## Control flow

There is no control flow in the offset header itself. It shapes consumer control flow by naming the MMIO addresses used in polling and read/modify/write sequences. The local 15.0.8 consumer reads TSC high/low/high under preemption control, returns ROM index/data offsets to generic ROM code, reads ROM clock-gating override bits when not on an APU, and branches on fields read from `SMUIO_MCM_CONFIG`.

I2C transfer logic in related SMUIO generations uses this style of offset table to disable clock gating, configure controller mode and timing, set target addresses, push data/command words, poll FIFO/status registers, clear interrupts, and abort stuck transactions. GPIO and ROM paths similarly use offsets for ordered command/status polling rather than arbitrary memory accesses.

## State and persistence behavior

The file represents hardware register locations. TSC count registers are live counter state. Software timer offsets address live interrupt/timer state and reset-request bits. Misc offsets address platform identity and scratch registers. I2C offsets address controller configuration, FIFO, interrupt, clear, abort, enable, status, timing, and component-identity state for two controllers. ROM offsets address SPI/ROM command, payload, busy, done, index, and data state. GPIO offsets address persistent pad configuration, strap observation, interrupt configuration/status, and SMIO controls.

Persistence depends on hardware reset domains and firmware/driver ownership. Scratch, GPIO, I2C timing, and ROM control registers may retain programmed values until reset or explicit reconfiguration. Status, busy/done, FIFO, interrupt, and clear registers are transient or side-effectful. The offset header cannot distinguish those semantics, so users must follow the owning block's programming sequence and avoid speculative writes.

## Dependencies and integration points

This header depends on the matching SMUIO 15.0.8 mask/default files and AMDGPU SOC15 register helper infrastructure. It integrates directly with `smuio_v15_0_8_funcs`, generic VBIOS ROM access, SMUIO GPU clock counter reads, platform topology detection, package-type selection, XGMI support detection, ROM clock-gating reporting, SMU-managed I2C buses, and GPIO/pinstrap discovery.

The two CKSVII2C windows line up with firmware interfaces that distinguish controller port 0 and port 1. The `smu15_driver_if_v15_0_8.h` interface comments identify CKSVII2C0/1 as selectable I2C controller ports, so these MMIO offsets are part of the bridge between driver-visible I2C transactions and SMU/board-management hardware.

## Risks

The main risk is address drift across close SMUIO generations. 15.0.8 includes I2C, ROM, and GPIO blocks that 15.0.0's offset file does not, shifts scratch-register offsets, omits `IO_SMUIO_PINSTRAP`, and lays out software timers differently. Using the wrong offset header can compile but access a different register because many names overlap.

Base-index values are uniformly 0 for I2C/ROM/GPIO and mixed for TSC/misc/timer, so callers should use the generated macros rather than hand-computing base addresses. The ROM software data window is long and sequential; any off-by-one offset can corrupt SPI command payloads or read the wrong data word. I2C controller 0 and 1 windows are repetitive; copying controller 0 offsets into controller 1 code would talk to the wrong bus. APU handling is also sensitive: `smuio_v15_0_8_get_clock_gating_state()` skips `CGTT_ROM_CLK_CTRL0` on APUs because that register is not available there.

## Test signals

Build validation should compile `amdgpu/smuio_v15_0_8.c` and any SMU I2C code that uses the 15.0.8 register map. Runtime validation should cover stable golden TSC reads, ROM index/data access, non-APU ROM clock-gating state reads, and expected package/topology/die/socket decoding from `SMUIO_MCM_CONFIG`.

I2C tests should exercise controller port 0 and port 1 separately, including clock setup, target address programming, STOP/RESTART behavior, FIFO status polling, abort-source handling, and recovery from stuck activity. ROM tests should cover software command payloads across the `ROM_SW_DATA_1..64` window and busy/done polling. GPIO tests should verify pad configuration, pinstrap reads, interrupt selection/status/acknowledge, and open-drain/SMIO enables. Generated-header tests should diff every offset and base index against the SMUIO 15.0.8 register database and compare nearby generations to catch accidental cross-generation reuse.
