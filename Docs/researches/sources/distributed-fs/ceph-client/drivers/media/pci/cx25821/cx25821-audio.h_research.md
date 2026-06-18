# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-audio.h

Purpose: defines audio DMA sizing constants used by the cx25821 core and ALSA support.

Important APIs and constants: `AUDIO_LINE_SIZE` is 128, `LINES_PER_BUFFER` is 15, `NUMBER_OF_PROGRAMS` is 8, and `MAX_AUDIO_DMA_BUFFER_SIZE` derives from RISC instruction sizes. It conditionally computes `MAX_BUFFER_PROGRAM_SIZE` using RISC NOOP instructions.

Control flow: no executable code. The constants guide buffer and RISC program sizing expectations for audio DMA paths.

State and persistence: no state. Values are compile-time constants.

Dependencies and integration points: included by `cx25821.h`, making these constants visible to core and audio compilation units. It aligns with SRAM audio cluster size definitions in `cx25821-sram.h` and RISC instruction generation in `cx25821-core.c`.

Risks: sizing constants must stay consistent with actual RISC program generation; undersizing can cause DMA program overflow, while oversizing wastes coherent memory. Some constants are legacy or not directly consumed by the current ALSA path.

Test signals: compile coverage and ALSA `hw_params`/capture tests that exercise maximum period counts and RISC program allocation.
