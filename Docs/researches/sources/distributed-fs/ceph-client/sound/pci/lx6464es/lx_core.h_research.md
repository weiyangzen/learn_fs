# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.h

## Purpose
This header declares the LX6464ES low-level DSP/PLX register interface, mailbox message structure, pipe/stream/buffer/gain/IRQ APIs, stream format constants, and pointer helper used by the ALSA-facing driver.

## Important APIs, Types, and Functions
Register enums define DSP ports such as CSM, CRM1-CRM12, interrupt/status, EtherSound config/MAC registers, and PLX ports such as mailboxes, doorbell, IRQ control, and chip select control. `struct lx_rmh` stores command/status lengths, status type, command index, and up to 12 command/status words. Function declarations expose all low-level operations implemented in `lx_core.c`. Inline wrappers `lx_stream_start/pause/stop()` call `lx_stream_set_state()`. `unpack_pointer()` splits DMA addresses into low/high 32-bit words.

## Control Flow
The header defines the call surface used by `lx6464es.c`: initialization uses version/clock/MAC/granularity/IRQ helpers; PCM prepare uses pipe and stream format helpers; trigger/IRQ uses stream state and buffer helpers; proc/control uses level helpers.

## State and Persistence
The only state type defined here is `struct lx_rmh`, embedded in `struct lx6464es`. It is reused for command submission and must be protected by `msg_lock`. Constants here encode firmware protocol state values but do not persist data.

## Dependencies and Integration Points
It includes `lx_defs.h` for opcodes, states, flags, and error constants. It forward-declares `struct lx6464es` to avoid circular dependencies and includes Linux interrupt types for IRQ prototypes.

## Risks
The register enum ordering must stay synchronized with offset arrays in `lx_core.c`. Duplicate `START_STATE`/`PAUSE_STATE` defines exist in the header and should be kept consistent if edited. DMA pointer splitting handles 32-bit and 64-bit hosts, but the main driver restricts DMA mask to 32-bit, so future 64-bit DMA changes require coordinated updates.

## Test Signals
Compile tests should detect prototype drift. Runtime tests should exercise every declared path indirectly: DSP version/clock/MAC during probe, pipe allocate/release during prepare/free, stream start/stop during trigger, buffer give on IRQ, level peak reads through proc, and IRQ enable/disable during module load/unload.
