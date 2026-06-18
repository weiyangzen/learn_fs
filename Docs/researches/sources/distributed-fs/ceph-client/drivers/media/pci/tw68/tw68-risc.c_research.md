
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-risc.c

## Purpose
This file builds TW68 DMA RISC programs for scatter-gather vb2 capture buffers. The programs synchronize odd/even fields, issue line DMA instructions across SG boundaries, and chain buffers by jump instructions.

## Important APIs, Types, And Functions
The exported implementation is `tw68_risc_buffer`. The internal generator is `tw68_risc_field`, which emits optional initial jumps, field sync instructions, `RISC_LINESTART`, and `RISC_INLINE` fragments. Disabled debug helpers `tw68_risc_decode` and `tw68_risc_program_dump` document instruction decoding.

## Control Flow
`tw68_buf_prepare` calls `tw68_risc_buffer` with field-specific offsets, bytes per line, padding, and line count. `tw68_risc_buffer` computes a conservative instruction count, allocates coherent DMA memory for the RISC program, emits top and/or bottom field programs, records `buf->jmp`, initializes the leading jump target to `buf->dma + 8`, and asserts that the generated program fits. `tw68_risc_field` walks the SG list, subtracting offsets until it reaches the target segment, then emits either a single line instruction or a fragmented line split across SG entries.

## State And Persistence
The generated program is stored in per-buffer coherent memory tracked by `struct tw68_buf` (`cpu`, `dma`, `jmp`, `size`). It persists for the lifetime of the vb2 buffer and is freed in `tw68_buf_finish`.

## Dependencies And Integration Points
The file depends on `tw68.h`, DMA coherent allocation, SG DMA addresses/lengths, and RISC opcodes from `tw68-reg.h`. `tw68-video.c` mutates `buf->jmp` and the first instruction to chain queued buffers and generate completion interrupts.

## Risks
SG traversal assumes valid SG entries for the requested offsets and line sizes. Instruction sizing is conservative but protected by `BUG_ON`, which is harsh if violated. Fragmented-line emission updates `offset = todo` after the final fragment, which should be reviewed carefully for padding behavior. The debug dump references a disabled `struct tw68_core` type, so it is not build-active.

## Test Signals
Stress capture with small, non-contiguous SG buffers, all supported field modes, and format/size changes that force program regeneration. Watch for DMA errors, PABORT/DMAPERR interrupts, buffer sequence continuity, and absence of coherent allocation leaks.
