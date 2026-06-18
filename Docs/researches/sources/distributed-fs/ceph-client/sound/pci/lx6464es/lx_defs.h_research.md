# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_defs.h

## Purpose
This header contains adapted LX6464ES/EtherSound firmware protocol definitions: clock-frequency thresholds, EtherSound configuration bitfields, interrupt masks, command opcodes, pipe/stream/buffer flags, stream format fields, and DSP/board error codes.

## Important APIs, Types, and Functions
Frequency macros classify 44.1/48 kHz EtherSound clock counters. `IOCR_*`, `FREQ_RATIO_*`, and `CONFES_*` define EtherSound configuration register fields. `MASK_SYS_STATUS_*`, `MASK_SYS_ASYNC_EVENTS`, and `MASK_SYS_PCI_EVENTS` describe interrupt/event bits. `enum cmd_mb_opcodes` defines MicroBlaze mailbox commands from system config through stream state. `enum pipe_state_t`, `enum stream_state_t`, `enum buffer_flags`, and `enum stream_flags` define firmware state/flag meanings. Error macros encode driver, board, resource, context, and realtime errors.

## Control Flow
The header has no executable flow, but `lx_core.c` uses these constants to construct commands, interpret responses, parse event masks, classify buffer slots, map stream/pipe states, and convert firmware errors into diagnostics.

## State and Persistence
Definitions here describe firmware-visible state, not driver-owned storage. They act as the persistent protocol contract between Linux driver source and LX firmware.

## Dependencies and Integration Points
It is included by `lx_core.h` and therefore by both LX implementation files. The constants integrate with PLX doorbell IRQs, MicroBlaze mailbox commands, EtherSound configuration, ALSA stream lifecycle, and proc peak reporting.

## Risks
Incorrect bit positions or masks would corrupt mailbox command object IDs, stream direction, buffer flags, or interrupt handling. Some comments indicate adapted vendor headers and legacy naming; edits should be validated against hardware documentation. Error codes mix warning/error/source/class/code fields, so callers must distinguish firmware-positive codes from Linux negative errno values.

## Test Signals
Probe should correctly configure 64 inputs/outputs and single frequency ratio. Clock detection should classify 44.1/48 kHz counters as expected. Buffer ask/give should identify valid/free/EOB slots through `BF_*` flags. Pipe/stream state polling should decode `PSTATE_*` and `SF_START` correctly. Injected or observed firmware errors should log the expected `ED_*`/`EB_*` class.
