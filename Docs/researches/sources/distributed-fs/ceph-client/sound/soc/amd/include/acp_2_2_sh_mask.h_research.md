# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_sh_mask.h

## Purpose
`acp_2_2_sh_mask.h` is the ACP 2.2 register bit-field companion to `acp_2_2_d.h`. It exports preprocessor constants for each documented field's mask and shift, using names like `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. The legacy AMD ACP audio header `sound/soc/amd/acp.h` includes this file after the offset map, giving ACP2.2-era driver code the field definitions needed to construct and decode MMIO register values.

There are no functions or executable statements. The file is an ABI map for DMA control, descriptor status, DSP memory windows and reset controls, DAGB/AXI bridge configuration and errors, global ACP reset/clock/power fields, interrupt masks/status/acks, semaphores, SRBM indexed access, firmware/timer/scratch registers, efuse and power-gating fields, voice wakeup controls, ACP memory sleep/shutdown fields, and I2S controller fields.

## Important APIs, types, and constants
The exported API is the mask/shift macro namespace. Important groups are:

- DMA channel fields for channels 0-15: `DMAChRst`, `DMAChRun`, `DMAChIOCEn`, `Circular_DMA_En`, `DMAChGracefulRstEn`, descriptor start index/count/current index, current transfer count, priority, terminal error, and error code.
- Global DMA fields: descriptor base address, maximum descriptors, channel status bitmap, and channel grouping.
- DSP0/DSP1/DSP2 fields: cache and noncache window offset/size, onion/garlic select, page enable, debug PC, NMI select, clock enable, soft reset, reset done, clock status, run-stall, halt-on-reset, wait mode, vector select, and debug registers.
- AXI2DAGB onion/garlic fields: data swap, multiple read/write request enables, max read burst, stall behavior, NACK/address-window violation checks, urgency, error status sources/overflow/valid bits, transaction performance counters, page group sizes, base addresses, snoop/target memory select, group enable, and ATU cache invalidation.
- ACP global fields: clock enable/status, JTAG enable, reference clock/stutter status, soft-reset control and done bits, SCLK sleep control, SMU mailbox, and future/reserved full-register fields.
- Interrupt/error fields: external interrupt enables/masks/status/acks, ACP error source status, DSP software interrupt trigger/control/status, DSP interrupt control/status for three DSPs, timeout values and counter enables, and external timers.
- Semaphore/SRBM fields: global semaphores 0-47, SRBM client base/read/cycle/index/data fields, and semaphore command/status/request address fields.
- Power and pad fields: efuse disable bits, PGFSM retain/config/write/read fields, ACP IP PGFSM access, I2S pin config, Azalia/I2S select, package/pad pull controls, BT UART pad select, memory shutdown/deep-sleep/wakeup request/status fields.
- I2S fields: speaker, mic/speaker, and Bluetooth I2S enable, RX/TX enable, clock control, channel enable, word length, ISR/IMR overrun/empty bits, FIFO flush/status, DMA address/control fields, and component parameter/version/type fields.

## Control flow
There is no local control flow. In use, the flow is:

1. A driver includes `acp.h`, receiving ACP2.2 offsets and bit-field masks.
2. The driver reads a register, clears or sets fields with these masks/shifts, and writes the result back.
3. Status paths decode fields such as DMA errors, interrupt status, byte counters, or power FSM state using the same constants.

The file does not provide field-preparation helpers; call sites must perform shifting/masking correctly or use kernel bitfield helpers when available.

## State and persistence behavior
No software state is stored. The macros describe mutable hardware state. Several fields are status/ack fields with write-one-to-clear style semantics in hardware; others control persistent runtime configuration such as DMA channel enable, circular DMA, DSP reset/run-stall, interrupt masks, DAGB address windows, and memory sleep/shutdown. Incorrect writes can outlive a single function call until reset or power-cycle.

## Dependencies and integration points
`sound/soc/amd/acp.h` is the direct in-tree include point. It combines this header with `acp_2_2_d.h`, then defines ACP DMA channel numbers, descriptor indices, SRAM banks, platform data, and DMA descriptor structures for older ACP PCM code. The mask names are tied to the `mm...` register offsets by naming convention rather than by typed structures.

The header is independent of the newer Pink Sardine `ps/acp63.h`, which uses byte-offset definitions from `acp63_chip_offset_byte.h`. Mixing ACP2.2 mask definitions with ACP6.3/7.x register offsets would be unsafe unless the register documentation explicitly guarantees compatibility for the specific field.

## Risks and edge cases
The largest risk is untyped bit manipulation. A field mask can be applied to the wrong register without compiler diagnostics. Repeated register banks also increase the chance of selecting a channel/DSP/I2S instance with a plausible but wrong macro name. Status and ack fields share masks for several interrupt registers; code must know whether it is reading status or writing an ack.

Hardware side effects are also significant. DMA run/reset bits, DSP reset/run-stall fields, interrupt enables, and memory power controls can stop audio streams or hang device initialization if programmed in the wrong order. Generated headers like this also tend to have limited direct unit coverage; many mistakes surface only on affected hardware.

## Test signals
Useful signals include:

- Build coverage for ACP2.2 legacy AMD ASoC drivers that include `acp.h`.
- Runtime ALSA playback/capture on ACP2.2 hardware, validating stream start/stop, period interrupts, byte counters, and error-free suspend/resume.
- IRQ storm/underrun/overrun tests around I2S FIFO and DMA IOC masks.
- Register trace or debugfs-style readback comparing programmed register values with expected masks/shifts.
- Static checks for raw literals that should use these macros, and for use of ACP2.2 macros in non-ACP2.2 driver paths.
