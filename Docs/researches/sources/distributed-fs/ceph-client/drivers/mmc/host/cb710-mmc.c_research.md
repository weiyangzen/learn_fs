# sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.c

## Purpose
`cb710-mmc.c` implements the MMC/SD portion of the ENE CB710 memory card reader driver. It is a PIO-only host driver built on the parent CB710 slot/chip abstraction, with many register behaviors inferred from hardware and the Windows driver. It handles command encoding, response decoding, data PIO, power sequencing, card-change IRQs, and platform-driver registration.

## Important APIs, Types, and Functions
The driver uses `struct cb710_mmc_reader` from `cb710-mmc.h` for active request, IRQ lock, finish work, and last power mode. MMC callbacks are `cb710_mmc_request`, `cb710_mmc_set_ios`, `cb710_mmc_get_ro`, and `cb710_mmc_get_cd`. Important helpers include `cb710_mmc_select_clock_divider`, `cb710_mmc_enable_irq`, `cb710_wait_for_event`, `cb710_wait_while_busy`, `cb710_mmc_set_transfer_size`, `cb710_mmc_fifo_hack`, `cb710_mmc_receive`, `cb710_mmc_send`, `cb710_encode_cmd_flags`, `cb710_receive_response`, `cb710_mmc_command`, `cb710_mmc_powerup`, `cb710_mmc_powerdown`, `cb710_mmc_irq_handler`, and init/exit/PM callbacks.

## Control Flow and State
Probe allocates an MMC host, reads PCI config to derive clock limits, initializes the finish work and IRQ lock, disables MMC IRQ sources, installs a CB710 slot IRQ handler, adds the MMC host, and enables card insertion status IRQs. Requests are synchronous in the request callback: set `reader->mrq`, enable test IRQs, run `cb710_mmc_command` for the main command and optional stop command, then schedule bottom-half work to call `mmc_request_done`.

Command execution waits for busy bits, writes command type and argument registers, resets event status, starts the command through config, waits for command-sent, decodes responses, and performs data transfer if present. Reads and writes use SG mapping iterators and 32-bit data-port helpers; reads apply a FIFO hack that discards two dwords to avoid prepended zeroes. Card-change IRQs acknowledge status and call `mmc_detect_change`.

## State and Persistence Behavior
State is volatile: active `mrq`, last power mode, IRQ enable register state, workqueue completion, and hardware config/status ports. No durable persistence exists. Power-up/down writes a sequence of magic config bits with delays and retries because register behavior is poorly understood. Clock divider state is programmed through PCI config register `0x40` using a source frequency from PCI config `0x48`.

## Dependencies and Integration Points
The driver depends on the CB710 core APIs (`cb710_read_port_*`, `cb710_write_port_*`, `cb710_modify_port_*`, slot/chip conversion, IRQ handler registration, dump helpers, SG data-port iterators), Linux MMC core, PCI config access, workqueues, delays, and platform-driver PM. It advertises 4-bit data, 3.2-3.4 V OCR, and a fixed busy timeout corresponding to its polling loops.

## Risks and Test Signals
Risks include guessed register semantics, fixed polling timeouts, no DMA, special-case transfer-size limits, FIFO workaround fragility, synchronous request work in MMC callback context, and interrupt enable locking that protects only one register. Test signals include probe/init, card insertion/removal IRQs, power-up retry behavior, 1-bit/4-bit mode, command responses including 136-bit shifts and opcode validation, supported/unsupported block sizes, read FIFO alignment cases, write PIO, suspend/resume IRQ disablement, and clean exit with pending finish work canceled.
