# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.h

## Purpose

This header declares the PCXHR low-level DSP/firmware/interrupt API and the RMH command protocol constants used by PCM, mixer, firmware, and board-specific files.

## Important APIs, Types, And Functions

- Firmware API: `pcxhr_reset_xilinx_com()`, `pcxhr_reset_dsp()`, `pcxhr_enable_dsp()`, and the Xilinx/eeprom/boot/main DSP load functions.
- `struct pcxhr_rmh` is the reusable DSP command/status container with command length, status length/type, command index, and fixed command/status buffers.
- The command enum defines all RMH command IDs, from version/support checks through pipe/stream/format/level/timecode operations.
- `pcxhr_init_rmh()`, `pcxhr_set_pipe_cmd_params()`, and `pcxhr_send_msg()` form the public command construction/sending API.
- IO register numbers, status selectors/results, codec register constants, codec chip-select constants, and pipe-control helpers are shared with the rest of the driver.
- IRQ entry points `pcxhr_interrupt()` and `pcxhr_threaded_irq()` are declared for PCI registration.

## Control Flow

Callers initialize an RMH with one enum command, OR in command-specific selectors, optionally append command words, then send with `pcxhr_send_msg()`. Pipe commands use `pcxhr_set_pipe_cmd_params()` to encode capture/playback, first-audio, stream index, and masks into the command word layout.

## State And Persistence

The header itself stores no state. It defines constants that determine the shape of mailbox commands and therefore the interpretation of hardware/DSP state.

## Dependencies And Integration Points

It forward-declares `struct firmware` and `struct pcxhr_mgr` and is included by all implementation files that interact with the DSP command layer. It also exposes codec constants used by mixer and source-selection logic.

## Risks

- Command enum order must stay synchronized with `pcxhr_dsp_cmds[]` in `pcxhr_core.c`.
- `PCXHR_SIZE_MAX_CMD`, status sizes, and mask constants define fixed buffer boundaries used by the RMH transport.
- Codec and register constants are raw hardware protocol values; accidental changes break board programming without compile-time symptoms.

## Test Signals

Compile-time coverage catches missing declarations, but real validation is command-level: firmware load, pipe allocation, stream format, mixer level, IEC958, and timecode commands must all complete with expected status lengths.
