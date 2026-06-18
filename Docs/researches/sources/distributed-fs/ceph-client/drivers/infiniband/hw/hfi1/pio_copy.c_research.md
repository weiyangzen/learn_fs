# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio_copy.c

## Purpose
`pio_copy.c` contains the low-level routines that write packet data into HFI1 PIO MMIO send-buffer space. It handles SOP versus non-SOP address spaces, block-aligned hardware write requirements, circular context wraparound, dangling bytes, and segmented packet construction.

## Important APIs, Types, And Functions
`pio_copy()` copies a complete aligned packet body after writing the PBC, using QWORD writes and padding the final PIO block. `seg_pio_copy_start()`, `seg_pio_copy_mid()`, and `seg_pio_copy_end()` support packet construction from multiple source fragments. Helpers such as `jcopy()`, `read_low_bytes()`, `read_extra_bytes()`, `merge_write8()`, `mid_copy_mix()`, and `mid_copy_straight()` maintain `pbuf->carry`, `carry_bytes`, and `qw_written` when source fragments are not naturally QWORD aligned.

## Control Flow
The complete-copy path writes the PBC to SOP space, writes QWORD data until the first block ends, switches into non-SOP space, wraps at `pbuf->end` if needed, writes remaining QWORD data, writes a dangling DWORD if present, pads to the next PIO block boundary, and decrements the per-CPU outstanding buffer count. The segmented path writes the PBC and initial aligned data, stores trailing bytes in `carry`, repeatedly merges or writes middle fragments while respecting SOP space and wraparound, then flushes any final carry and pads the block in `seg_pio_copy_end()`.

## State And Persistence
The routines mutate only the supplied `pio_buf`: `qw_written`, `carry`, `carry_bytes`, and implicit outstanding-buffer accounting in the owning send context. The hardware-visible state is the MMIO PIO buffer contents. The functions assume `preempt_disable()` was performed during buffer allocation and finish by decrementing `buffers_allocated` and enabling preemption.

## Dependencies And Integration Points
The code depends on `struct pio_buf` from `pio.h`, `writeq()` MMIO semantics, the HFI1 PIO address layout where SOP space is offset by half the PIO aperture, and send-context size/end metadata. It is called by verbs/PIO send paths after `sc_buffer_alloc()` succeeds.

## Risks
The functions rely on strict alignment and size contracts: `pio_copy()` expects an 8-byte-aligned source and a DWORD count, while segmented helpers tolerate misaligned middle fragments through carry handling. Incorrect `qw_written` or carry accounting would corrupt packet boundaries. Pointer arithmetic on `void *` is a kernel extension. The final preemption enable assumes each buffer allocation has disabled preemption exactly once.

## Test Signals
Test single-block packets, multi-block packets, exact SOP block endings, context wraparound, odd DWORD counts, segmented fragments smaller than 8 bytes, misaligned middle fragments, carry flush at end, padding behavior, and outstanding buffer counter balance under all copy paths.
