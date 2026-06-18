# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdio.c

## Purpose

`meson-mx-sdio.c` implements an older Amlogic Meson6/Meson8/Meson8b SDIO/MMC host controller driver. It supports a controller node with child `mmc-slot` devices, one active slot, DMA-mapped transfers, command timeout handling, response decoding, and an internally registered divider clock.

## Important APIs, Types, And Functions

- Register macros define SDIO argument, send, configuration, IRQ status/control, multi-slot control, DMA address, and extended data-length registers.
- `struct meson_mx_mmc_host_clkc` stores a fixed divide-by-2 clock and a configurable divider clock.
- `struct meson_mx_mmc_host` stores controller device, cfg divider clock, regmap, IRQ/spinlock, command timeout timer, slot id, MMC host, active request/command, and sticky setup error.
- `meson_mx_mmc_start_cmd()` builds SEND/EXT values, chooses response bit count, busy checking, repeated package count, data direction, slot selection, interrupt enable/ack, argument, and timeout timer.
- `meson_mx_mmc_request()` maps DMA, records the request, writes the data DMA address, and starts SBC or main command.
- `meson_mx_mmc_read_response()` reads short and long responses by programming response read index fields.
- `meson_mx_mmc_process_cmd_irq()`, `meson_mx_mmc_irq()`, and `meson_mx_mmc_irq_thread()` validate CRC bits, ack interrupts, unmap DMA, set bytes transferred, chain next command, and complete requests.
- `meson_mx_mmc_timeout()` disables command interrupts, records timeout state, and completes the request if the IRQ did not already do it.
- `meson_mx_mmc_slot_pdev()` creates the first `mmc-slot` child platform device and warns about unsupported additional slots.
- `meson_mx_mmc_register_clk()` registers a fixed-div2 clock and configurable divider backed by `MESON_MX_SDIO_CONF`.
- `meson_mx_mmc_probe()` maps resources, creates the slot child, allocates the host on the slot device, initializes regmap/IRQ/clock/config, resets hardware, and adds the host.

## Control Flow And State

The controller probe creates a child slot platform device and allocates the MMC host under that slot. It initializes the SDIO configuration register with argument width, endian, write timing, and CRC status patterns, soft-resets the controller, parses the slot, and adds the host.

Requests persist in `host->mrq` and `host->cmd`. Data SGs must be 32-bit aligned and are DMA-mapped before start. If an SBC exists, it is sent first; otherwise the main command is sent. Command start selects the slot, enables command-done IRQ, clears pending command IRQ, writes argument and transfer size, starts the command, and arms a per-command timer. The hard IRQ reads status and SEND configuration, processes command completion if present, and acks all pending IRQs. The thread deletes the timer, unmaps data, sets bytes transferred, and either starts the next command (main after CMD23 or stop after multi-block) or completes the request.

The timeout path disables command interrupts under `irq_lock`, checks if another path already cleared `host->cmd`, logs status, sets `-ETIMEDOUT`, soft-resets during request completion, and completes the request.

## Dependencies And Integration Points

The driver depends on platform/OF infrastructure, child node creation through `of_platform_device_create()`, regmap, clocks, DMA mapping, timers, threaded IRQs, regulators, GPIO CD/WP helpers, and MMC core parsing. It matches `"amlogic,meson8-sdio"` and `"amlogic,meson8b-sdio"`.

## Risks And Edge Cases

- Multiple hardware slots are not really supported; only the first `mmc-slot` child is registered.
- `host->error` is sticky after `set_ios` or mapping failures and can fail later requests until reset by a successful path.
- Only the first SG entry is alignment-checked before mapping, while the mapped request may contain more entries.
- Timeout and IRQ paths coordinate via `host->cmd` and interrupt disable; races are handled defensively but remain critical.
- The driver sets `bytes_xfered` to the full request size whenever data command IRQ completes, relying on CRC/status validation.
- Long response bit shifting is custom and must remain aligned with hardware response FIFO semantics.

## Test Signals

Validation should cover one-slot DT probing, warning on multiple slots, clock divider registration/rate changes, 1-bit and 4-bit bus modes, regulator OCR changes, aligned DMA reads/writes, rejection of unaligned first SG, command timeout timer, duplicate command IRQ tolerance, CRC error detection for response and data, SBC/main/stop chaining, card detect/write protect GPIOs, and remove-time timer/clock/device cleanup.
