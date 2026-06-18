# sources/distributed-fs/ceph-client/sound/hda/core/controller.c

## Purpose
`controller.c` implements shared low-level HD-audio controller operations: CORB/RIRB command transport, PIO immediate command fallback, RIRB response parsing, capability discovery, link reset, interrupt control, chip start/stop, stream IRQ dispatch, DMA page allocation, and basic codec-link power bookkeeping.

## Important APIs, Types, and Functions
Exports include `snd_hdac_bus_init_cmd_io()`, `snd_hdac_bus_stop_cmd_io()`, `snd_hdac_bus_update_rirb()`, `snd_hdac_bus_send_cmd()`, `snd_hdac_bus_get_response()`, `snd_hdac_bus_parse_capabilities()`, `snd_hdac_bus_enter_link_reset()`, `snd_hdac_bus_exit_link_reset()`, `snd_hdac_bus_reset_link()`, `snd_hdac_bus_init_chip()`, `snd_hdac_bus_stop_chip()`, `snd_hdac_bus_handle_stream_irq()`, `snd_hdac_bus_alloc_stream_pages()`, `snd_hdac_bus_free_stream_pages()`, and `snd_hdac_bus_link_power()`.

## Control Flow
Chip init resets the link, clears interrupts, initializes command I/O, enables interrupts, programs position buffer DMA, and marks `chip_init`. Command I/O sets up CORB/RIRB in one DMA page. RIRB update consumes hardware write pointer entries, routes unsolicited events, wakes response waiters, and logs spurious responses. Link reset toggles `GCTL.RESET` with spec delays and reads `STATESTS` into `codec_mask`.

## State and Persistence Behavior
The bus owns CORB/RIRB buffers, response counters, last commands, position buffers, stream BDL pages, capability pointers, codec mask, and `chip_init`. DMA pages remain allocated until controller teardown. Command DMA state is also manipulated by the extended core.

## Dependencies and Integration Points
Controllers call these helpers during probe, PM resume, suspend, shutdown, and IRQ handling. The code depends on HDA register definitions, DMA allocation, spinlocks, waitqueues, and stream objects from `stream.c`.

## Risks
Hardware timing is delicate: CORBRP reset, RIRB waits, link reset delays, and interrupt clearing differ by controller. Polling and PIO command modes must stay coherent with bus flags. Stream IRQ ack callbacks must not run for stopped or unbound streams.

## Test Signals
Test CORB/RIRB command/response success and timeout paths, PIO mode, unsolicited events, codec discovery, capability parsing, chip init/stop idempotence, stream IRQ handling, DMA allocation/free, and PM cycles that reinitialize command buffers.
