# sources/distributed-fs/ceph-client/sound/soc/amd/include/acp_2_2_d.h

## Purpose
`acp_2_2_d.h` is a generated-style ACP 2.2 register address header. It exports only preprocessor constants named `mm...`, mapping ACP hardware register names to dword register offsets in the ACP 2.2 MMIO/register namespace. It is included by `sound/soc/amd/acp.h`, which is then consumed by the older ACP PCM/I2S DMA platform code. There are no functions, structs, or executable control paths in this file; its behavior is entirely defined by the numeric ABI it gives to MMIO access sites.

The file covers the ACP 2.2 hardware block at a broad level: 16 DMA channels, DMA descriptor tables and status, three DSP control/register windows, AXI-to-DAGB onion/garlic transport controls, DAGB page groups, ACP clock/reset/power/status registers, external and DSP interrupt registers, semaphores, SRBM client indexed access, firmware/timer/scratch registers, efuse and power FSM registers, voice wakeup registers, memory sleep/shutdown controls, and I2S speaker/microphone/Bluetooth controller registers.

## Important APIs, types, and constants
The exported API is the `mmACP_*` and `mmI2S_*` macro namespace. Major groups are:

- `mmACP_DMA_CNTL_0` through `mmACP_DMA_CNTL_15`, plus `mmACP_DMA_DSCR_STRT_IDX_*`, `mmACP_DMA_DSCR_CNT_*`, `mmACP_DMA_PRIO_*`, `mmACP_DMA_CUR_DSCR_*`, `mmACP_DMA_CUR_TRANS_CNT_*`, and `mmACP_DMA_ERR_STS_*`, define the per-channel DMA control/status register map.
- `mmACP_DMA_DESC_BASE_ADDR`, `mmACP_DMA_DESC_MAX_NUM_DSCR`, `mmACP_DMA_CH_STS`, and `mmACP_DMA_CH_GROUP` define global DMA descriptor and grouping registers.
- `mmACP_DSP{0,1,2}_CACHE_OFFSET*`, `CACHE_SIZE*`, `NONCACHE_OFFSET*`, `NONCACHE_SIZE*`, `DEBUG_PC`, `CLKRST_CNTL`, `RUNSTALL`, `WAIT_MODE`, `VECT_SEL`, and `DEBUG_REG*` define repeated register banks for three DSP instances.
- `mmACP_AXI2DAGB_ONION_*`, `mmACP_AXI2DAGB_GARLIC_*`, and `mmACP_DAGB_*` define data-fabric bridge setup, error status, counters, page size/base groups, and ATU control.
- `mmACP_CONTROL`, `mmACP_STATUS`, `mmACP_SOFT_RESET`, `mmACP_PwrMgmt_CNTL`, `mmACP_SMU_MAILBOX`, and `mmACP_PGFSM_*` define ACP-wide power, reset, status, and power-gating controls.
- `mmACP_EXTERNAL_INTR_*`, `mmACP_DSP_SW_INTR_*`, and `mmACP_DSP{0,1,2}_INTR_*` define host/DSP interrupt enable, status, ack, and timeout registers.
- `mmACP_I2SSP_*`, `mmACP_I2SMICSP_*`, and `mmACP_I2SBT_*` define the I2S speaker, mic/speaker, and Bluetooth banks.

This file intentionally does not expose typed helpers. Callers combine these offsets with bit masks from `acp_2_2_sh_mask.h` and local MMIO helpers such as `readl()`/`writel()`.

## Control flow
There is no runtime control flow. The effective control flow is at include/preprocessor time:

1. `sound/soc/amd/acp.h` includes this header.
2. ACP legacy platform code references the register-offset macros while programming DMA descriptors, I2S controllers, power tiles, reset, and counters.
3. The compiler substitutes the numeric offsets directly into MMIO access expressions.

The file therefore must be treated as a hardware contract, not as logic that can be refactored independently.

## State and persistence behavior
The header stores no software state. It names hardware state that persists in ACP registers while the device is powered. The registers named here include mutable state such as current DMA descriptor indices, current transfer counts, interrupt status/ack bits, firmware status, timer counts, scratch registers, byte counters, power FSM status, wakeup state, and I2S FIFO/status fields. Persistence and reset semantics are hardware-defined and handled by the drivers that use these addresses.

## Dependencies and integration points
The immediate integration point is `sources/distributed-fs/ceph-client/sound/soc/amd/acp.h`, which includes this header together with `acp_2_2_sh_mask.h`. The older ACP PCM DMA code relies on both headers to program DMA channels and I2S controller instances. The offset values are dword register indices in the ACP 2.2 register documentation style, so call sites must use the same address-unit convention expected by the local register accessor macros/helpers.

This file is independent of the newer `ps/acp63.h` path. `acp63.h` includes a different offset source, `<sound/acp63_chip_offset_byte.h>`, for ACP6.3/7.x byte offsets.

## Risks and edge cases
The main risk is silent hardware misprogramming if any offset is wrong, if a caller treats a dword offset as a byte offset, or if an ACP generation mismatch causes ACP2.2 offsets to be used on a newer block. Because these macros are untyped, the compiler cannot catch use of the wrong register bank or read/write direction. The repeated per-channel and per-DSP patterns also make copy/paste mistakes hard to see in review.

Another risk is stale generated documentation: this header carries an MIT license and 2014 AMD copyright, while newer ACP drivers use separate ACP6.3/7.x register definitions. Maintainers should avoid extending this file for unrelated ACP generations unless the hardware documentation confirms binary compatibility.

## Test signals
Useful validation is mostly integration or hardware-facing:

- Build coverage for drivers that include `sound/soc/amd/acp.h` catches missing or renamed macros.
- Boot/probe tests on ACP2.2-era hardware should confirm ACP power-on/reset, DMA descriptor programming, and I2S playback/capture still work.
- ALSA PCM playback/capture tests exercise the DMA/I2S offsets indirectly through stream startup, period interrupts, byte counters, underrun/overrun behavior, and shutdown.
- Register readback/debug traces can compare accessed offsets against ACP 2.2 hardware documentation.
