# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670-dsp.h

## Purpose

`rt5670-dsp.h` is a compact private interface for the RT5670 codec DSP command registers. It defines the DSP control register addresses, command encodings, command-format bitfields, clock selectors, busy/read-write/data-length flags, and a small parameter struct used to represent a DSP command transaction. In this source snapshot, `rt5670.c` includes the header and exposes DSP routing widgets, while the header provides the register-level vocabulary for any companion DSP command code.

## Important APIs, Types, and Constants

`RT5670_DSP_CTRL1` through `RT5670_DSP_CTRL5` name the contiguous DSP control registers at `0xe0` through `0xe4`.

The `RT5670_DSP_CMD_*` constants encode command opcodes in the high byte of DSP control 1: patch entry, memory write, memory read, register read, register write, high data address, and low data address. `RT5670_DSP_CMD_MASK` covers the opcode field.

The clock field constants `RT5670_DSP_CLK_MASK`, `RT5670_DSP_CLK_SFT`, and `RT5670_DSP_CLK_768K/384K/192K/96K` define the DSP command clock selection. `RT5670_DSP_BUSY_MASK`, `RT5670_DSP_RW_MASK`, `RT5670_DSP_DL_MASK`, `RT5670_DSP_DL_0` through `RT5670_DSP_DL_3`, `RT5670_DSP_I2C_AL_16`, and `RT5670_DSP_CMD_EN` define command status, direction, data length, I2C address length, and enable bits.

`struct rt5670_dsp_param` groups a DSP command format word, address, data, and 8-bit command code. It is the natural data carrier for command submission helpers, firmware patch loops, or register/memory access routines.

## Control Flow Role

This header does not implement control flow. Its constants are intended to support a sequence where a caller formats a command, programs address/data registers, sets clock/read-write/data-length fields, enables the command, and polls the busy bit. In `rt5670.c`, the DSP appears mostly in DAPM routing (`I2S DSP`, `Audio DSP`, `DSP UL Mux`, `DSP DL Mux`, `RxDP Mux`, `TxDP_ADC`, and `TxDC_DAC`) rather than explicit command transactions.

## State and Persistence Behavior

The header has no persistent state. DSP command state lives in codec hardware registers and, if used by implementation code, would be transient around command execution. The busy bit and control registers should generally be considered volatile; `rt5670.c` marks the DSP control registers volatile and readable in its regmap callbacks, preventing cached reads from hiding hardware progress.

## Dependencies and Integration Points

The file is included by `rt5670.c` and is tied to RT5670 register layout. It depends only on standard kernel integer typedef availability through the including context. Its register addresses are included in `rt5670.c` readable/volatile regmap handling, which is the key integration point even if no DSP command helper is present in this file set.

## Risks and Edge Cases

DSP command fields are hardware-protocol sensitive. Incorrect opcodes, address length, data length, or clock selection can lead to hung commands, wrong DSP memory/register writes, or reads of stale data. Any command routine using this header needs bounded busy polling and error handling; otherwise a hardware fault can become an unbounded delay. Since the header is small and rarely edited, the main risk is drift from hardware documentation or from the DSP firmware loader expected by machine-specific code.

## Test Signals

Useful signals include static checks that every `RT5670_DSP_CTRL*` register is considered volatile/readable in the regmap callbacks, successful DSP route activation in DAPM, and any platform DSP firmware or patch routine being able to perform memory/register read-write commands with bounded busy waits. Audio tests should verify DSP bypass and non-bypass routes if firmware support is present.
