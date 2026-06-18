# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_a2150.c

## Purpose
`ni_at_a2150.c` is a legacy ISA Comedi driver for NI AT-A2150C/S analog input boards. It supports single-sample reads and, when valid IRQ and DMA options are supplied, asynchronous timed acquisition using ISA DMA.

## Important APIs, Types, And Functions
`struct a2150_board` describes clock periods and maximum AI speed for the C and S variants. `struct a2150_private` stores ISA DMA state, remaining sample count, IRQ/DMA register shadow bits, and configuration register shadow bits. `a2150_probe()` identifies the board from `STATUS_REG` ID bits. `a2150_get_timing()` rounds requested scan periods to board clock/divisor combinations and updates config bits. `a2150_set_chanlist()` and `a2150_ai_check_chanlist()` enforce hardware channel grouping constraints.

Command validation and execution are in `a2150_ai_cmdtest()` and `a2150_ai_cmd()`. Interrupt-driven DMA completion is handled by `a2150_interrupt()`. Single reads use `a2150_ai_rinsn()` and `a2150_ai_eoc()`. Resource helpers are `a2150_alloc_irq_and_dma()`, `a2150_free_dma()`, `a2150_attach()`, `a2150_detach()`, and `a2150_cancel()`.

## Control Flow
Attach allocates private state, requests the ISA I/O region, probes board ID, optionally allocates IRQ plus one ISA DMA buffer, allocates an 8254 pacer, creates one AI subdevice, powers and calibrates the ADC path, waits for offset calibration to finish, and enables analog input channels. If no IRQ/DMA is available, the AI subdevice remains instruction-only.

For a command, `a2150_ai_cmd()` cancels/clears FIFO state, programs channel grouping and AC/DC coupling, rounds timing, writes config bits, calculates remaining samples, disables and programs ISA DMA, clears pending terminal-count interrupt, enables board DMA/interrupts, loads counter 2 for the 72-period settling delay, configures software or external trigger bits, and starts acquisition for `TRIG_NOW`. The ISR validates interrupt status and DMA terminal count, disables DMA to get residue, computes received samples and the next transfer size, converts two's-complement ADC samples to unsigned, writes them to the Comedi buffer, reprograms DMA if needed, handles EOA, dispatches events, and clears the terminal count interrupt.

## State And Persistence
State lives in `devpriv->config_bits`, `devpriv->irq_dma_bits`, the ISA DMA descriptor, and `devpriv->count`. The 8254 pacer and board registers hold timing/trigger state. Detach powers down analog/digital circuitry, frees DMA, and releases legacy resources.

## Dependencies And Integration Points
The driver depends on ISA I/O port access, `comedi_isadma`, `comedi_8254`, Linux IRQ APIs, Comedi command validation helpers, and Comedi async buffers. It exposes only one AI subdevice.

## Risks
Command path requires both IRQ and DMA; a misconfigured user gets no async capability. `a2150_ai_cmd()` reads `cmd->chanlist[2]` while setting AC coupling for channels 2/3, which is risky for one- or two-channel commands and relies on surrounding assumptions. DMA residue handling is subtle for external stop triggers. Timing rounding mutates both requested timing and hardware shadow bits. The code returns `-1` in several paths rather than specific errno values.

## Test Signals
Useful tests include board ID probe for C/S, invalid IRQ/DMA rejection, calibration timeout behavior, timing rounding across all master clocks/divisors and round modes, chanlist validation for 1/2/4 channels, instruction read discarding 36 filter-delay samples, command setup for external versus software start, DMA transfer sizing, residue handling, EOA on count exhaustion, overflow/error event generation, cancel disabling board and host DMA, and detach powerdown.
