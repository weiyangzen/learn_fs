# subset-b-003426 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_offset.h

## Purpose

`smuio_15_0_0_offset.h` is the generated SMUIO 15.0.0 register offset map. It exports `reg...` register address constants and matching `reg..._BASE_IDX` constants for AMDGPU SOC15 register helpers. It contains no functions, types, storage, or runtime control flow. The matching `smuio_15_0_0_sh_mask.h` supplies field positions and masks for the registers named here.

This SMUIO 15.0.0 offset file is smaller than the 14.0.2 and 15.0.8 maps. It covers misc, reset, TSC, and software timer blocks only. In the local source tree, `amdgpu/smuio_v15_0_0.c` includes this file and uses the TSC count offsets to implement `get_gpu_clock_counter`.

## Important APIs, types, and macros

The exported API is a list of `#define` constants. The suffixless `reg*` macros provide register offsets suitable for `SOC15_REG_OFFSET(SMUIO, instance, regNAME)` and `RREG32_SOC15(SMUIO, instance, regNAME)`. The `_BASE_IDX` constants select the generated base index for the address block. Most entries in this file use base index 1 for misc/TSC/swtimer registers, except `regSMUIO_MCM_CONFIG` and `regSMUIO_GFX_MISC_CNTL`, which use base index 0.

The misc block has base address comment `0x5a000` and defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, eight scratch registers, and `IO_SMUIO_PINSTRAP`. Scratch register offsets run consecutively from `0x01c6` through `0x01cd`, with pinstrap at `0x01ce`.

The reset block has base address comment `0x5a300` and defines only `SMUIO_GFX_MISC_CNTL` at offset `0x00c5`. The companion mask header gives this register fields for GFX cold-vs-gfxoff and GFXOFF status.

The TSC block has base address comment `0x5a8a0` and defines `PWROK_REFCLK_GAP_CYCLES`, golden TSC increment upper/lower, golden TSC count upper/lower, SOC golden TSC shadow upper/lower, and `SOC_GAP_PWROK`. These are the direct inputs for the 64-bit counter read in `smuio_v15_0_0_get_gpu_clock_counter()`.

The software timer block has base address comment `0x5aca8` and defines `PWR_VIRT_RESET_REQ`, display timer 1 and 2 control/debug/elapsed-control registers, global timer control, and `PWR_IH_CONTROL`. Compared with 14.0.2-style timer masks, 15.0.0 adds elapsed-control offsets for both display timers.

## Control flow

The file has no branches or executable operations. It affects control flow only when compiled into AMDGPU register-access paths. The concrete local consumer, `smuio_v15_0_0_get_gpu_clock_counter()`, reads `regGOLDEN_TSC_COUNT_UPPER`, `regGOLDEN_TSC_COUNT_LOWER`, and the upper half again under `preempt_disable()` to avoid returning a torn clock value if the low half rolls between reads.

## State and persistence behavior

All represented state lives in SMUIO hardware registers. Misc registers expose platform identity, IP discovery, scratchpad persistence, and strap state. `SMUIO_GFX_MISC_CNTL` exposes reset/power-state status and control-like bits for GFXOFF handling. TSC registers expose live timebase count/increment/shadow state. Software timer registers expose FLR request, timer interrupt count/config/status/elapsed state, pulse shape, and interrupt-handler credit/trigger control.

The header itself persists nothing and cannot enforce read/write semantics. Consumers must respect whether a register is read-only identity, writable scratch/config, command-like, status, sticky, or acknowledge-on-write. Offset correctness is essential because the same `regNAME` is passed to generic SOC15 helpers that compute final MMIO addresses from the IP block, instance, base index, and offset.

## Dependencies and integration points

This header depends on the generated SMUIO 15.0.0 mask/default headers and AMDGPU SOC15 register helper infrastructure. It is integrated by `amdgpu/smuio_v15_0_0.c` through `#include "smuio/smuio_15_0_0_offset.h"` and by any other SMUIO 15.0.0 code that reads package, TSC, reset, scratch, or timer registers.

The offset definitions are part of the ABI between the driver and the hardware register database. They also integrate with IP discovery: `IP_DISCOVERY_VERSION` can be read to validate discovered IP versions, while base-index values tell SOC15 helper macros which generated base address slot should be used.

## Risks

Wrong offsets or base indices can direct reads and writes to the wrong SMUIO register, which is worse than a wrong field mask because it can corrupt unrelated hardware state. Base-index drift is a specific risk: `SMUIO_MCM_CONFIG` uses base index 0 while many neighboring misc entries use base index 1, so assuming one base index for the whole commented block would be incorrect.

The TSC count registers are order-sensitive in consumers. If the upper/lower offsets are swapped or stale, clock readings can jump, repeat, or appear non-monotonic. The timer offset sequence differs from 15.0.8, where timer 2 and global/IH offsets shift because elapsed-control registers are absent; mixing 15.0.0 and 15.0.8 offset/mask sets would decode or program the wrong timer registers. The reset block has a single register, so a missing include or wrong ASIC match might compile but silently skip expected GFXOFF behavior.

## Test signals

Build coverage should include `amdgpu/smuio_v15_0_0.c` and any table that attaches `smuio_v15_0_0_funcs` to ASIC discovery. Runtime validation should check monotonic GPU clock counter values, correct high/low rollover handling, successful reads of IP discovery and scratch registers, and expected `SMUIO_GFX_MISC_CNTL` status on supported hardware.

Register database validation should compare every `reg...` value and `_BASE_IDX` against the authoritative SMUIO 15.0.0 specification. Hardware timer validation should verify display timer interrupts, elapsed-control behavior, and `PWR_IH_CONTROL` trigger/credit handling if those paths are enabled. A negative test signal is any compile error in `REG_GET_FIELD` or `RREG32_SOC15` consumers after changing names, because these generated names are used directly rather than through wrapper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_sh_mask.h

## Purpose

`smuio_15_0_0_sh_mask.h` is the generated SMUIO 15.0.0 field-layout companion to `smuio_15_0_0_offset.h`. It defines shifts and masks for misc, reset, TSC, and software timer registers. It is declarative register ABI data only; there are no C functions, local variables, structs, function pointers, or executable statements.

The local AMDGPU integration point is `amdgpu/smuio_v15_0_0.c`, which includes this header with the offset file. That C file currently uses only the TSC count offsets directly, but this mask header provides the field definitions needed by any SMUIO 15.0.0 code using `REG_GET_FIELD` and `REG_SET_FIELD`.

## Important APIs, types, and macro families

The misc block defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, scratch registers 0 through 7, and `IO_SMUIO_PINSTRAP`. In this generation, `SMUIO_MCM_CONFIG` exposes `DIE_ID`, `PKG_TYPE`, `SOCKET_ID`, `CONSOLE_K`, `CONSOLE_A`, and `PKG_SUBTYPE`. Notably, `PKG_TYPE` occupies mask `0x0000003c`, `SOCKET_ID` is a single bit at mask `0x00000100`, and `PKG_SUBTYPE` is at bit 18. These layouts differ from older generated files and must be paired with 15.0.0 consumers.

The pinstrap register defines audio port connection and audio strap fields. Scratch registers and IP discovery are full-width values. The scratch registers form a simple 8-word MMIO scratchpad surface that firmware and driver paths may use depending on platform policy.

The reset block defines `SMUIO_GFX_MISC_CNTL` with `SMU_GFX_cold_vs_gfxoff` and `PWR_GFXOFF_STATUS` fields. The status field spans mask `0x00000006`, so consumers should decode it as a small value rather than a single Boolean unless a specific bit is intended.

The TSC block defines the same timebase register fields as neighboring SMUIO generations: pre/post PWROK reference-clock gap cycles, 24-bit upper and 32-bit lower golden TSC increment halves, 24-bit upper and 32-bit lower count halves, SOC golden TSC shadow halves, and a one-bit SOC gap power-good field.

The software timer block defines `PWR_VIRT_RESET_REQ`, display timer 1 and 2 control/debug/elapsed-control registers, global timer control, and `PWR_IH_CONTROL`. Control registers expose a 25-bit interrupt count plus enable, disable, mask, status-ack, type, and mode bits. Debug registers expose running, status, interrupt, and run-value fields. The elapsed-control registers expose a 25-bit elapsed-time count and comparison-enable bit. `PWR_IH_CONTROL` defines max credit, display timer trigger masks, display timer 2 trigger masks, and clock-gate enable.

## Control flow

The header itself has no control flow. Consumer control flow comes from MMIO read/modify/write and polling logic. For example, a timer handler can read a control/debug register, use these masks to test status, acknowledge with the `DISP_TIMER_INT_STAT_AK` field, and configure the next count. A reset path can set the VF or PF FLR request bits in `PWR_VIRT_RESET_REQ`. A platform-identification path can read `SMUIO_MCM_CONFIG` and branch on die, package, socket, console, or subtype fields.

## State and persistence behavior

This file describes persistent and live hardware register state. `SMUIO_MCM_CONFIG`, pinstrap, and IP discovery are identity/configuration state. Scratch registers can persist driver/firmware scratch values across portions of initialization until reset or overwrite. `SMUIO_GFX_MISC_CNTL` exposes GFXOFF-related state. TSC registers are live counters and increment configuration. Timer registers hold programmed interrupt counts, elapsed counts, modes, masks, status, acknowledge state, and trigger routing. `PWR_VIRT_RESET_REQ` carries reset request bits that may be consumed asynchronously by hardware or firmware.

The file cannot encode whether fields are read-only, write-one-to-clear, sticky, or reserved. Because timer and reset registers are side-effect sensitive, callers must use the documented SMUIO programming sequence, not just raw mask manipulation. For TSC reads, consumers must avoid torn high/low reads; the local `smuio_v15_0_0_get_gpu_clock_counter()` implements the usual high-low-high sequence.

## Dependencies and integration points

The header depends on the generated offset map for SMUIO 15.0.0 and the AMDGPU register helper macros that concatenate register and field names inside `REG_GET_FIELD` and `REG_SET_FIELD`. It integrates with ASIC-specific SMUIO callback setup, power-management and GFXOFF code, reset/virtualization flows that request PF/VF FLR, display/power timer interrupt routing, and platform topology discovery.

It is important that code using `SMUIO_MCM_CONFIG` field names be generation-aware. Other local SMUIO files expose topology or package fields differently, and `smuio_v15_0_8.c` expects a `TOPOLOGY_ID` field in its own matching mask file. This 15.0.0 mask file does not define that field.

## Risks

The largest risk is generation mismatch. A caller built against this file but using 15.0.8 or 14.0.2 offsets could write timer elapsed-control fields into a different register or decode package/socket bits incorrectly. Conversely, code copied from `smuio_v15_0_8.c` that expects `SMUIO_MCM_CONFIG__TOPOLOGY_ID` would not compile with this header and should not be papered over with hard-coded masks unless the hardware spec confirms them.

Timer registers have many adjacent one-bit controls near the high end of the word. Off-by-one shifts can enable instead of disable, mask instead of acknowledge, or configure interrupt type/mode incorrectly. `PWR_VIRT_RESET_REQ` divides VF and PF FLR bits across a broad mask and bit 31; wrong writes here can request resets for the wrong function. `PWR_IH_CONTROL` clock gating and trigger masks affect interrupt delivery, so reserved-bit writes may cause lost or spurious power/display timer events.

## Test signals

Compile tests should cover all 15.0.0 SMUIO consumers and any code using `REG_GET_FIELD(data, SMUIO_MCM_CONFIG, ...)` with this header. Runtime tests should verify monotonic TSC reads, correct `SMUIO_MCM_CONFIG` decode for die/package/socket/subtype, and expected GFXOFF status decoding. Timer validation should program display timer counts and elapsed comparisons, observe interrupt/debug status, acknowledge status, and verify `PWR_IH_CONTROL` routing.

Reset validation should exercise PF/VF FLR paths on hardware or simulation that exposes `PWR_VIRT_RESET_REQ`. Generated-header validation should compare every shift and mask against the SMUIO 15.0.0 register database and should specifically check fields whose positions differ from 14.0.2 or 15.0.8.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_offset.h -->
