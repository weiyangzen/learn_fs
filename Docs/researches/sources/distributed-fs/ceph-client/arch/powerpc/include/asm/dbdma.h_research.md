## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbdma.h

Purpose: defines Apple Descriptor-Based DMA controller registers, command descriptors, command encodings, and reset/stop macros for Power Macintosh hardware.

Important APIs/types/functions: `struct dbdma_regs`, `struct dbdma_cmd`, command values such as `OUTPUT_MORE`, `INPUT_LAST`, `DBDMA_STOP`, key/interrupt/branch/wait field macros, `DBDMA_ALIGN()`, `DBDMA_DO_STOP()`, and `DBDMA_DO_RESET()`.

Control flow: drivers build little-endian command rings and program controller registers. Stop/reset macros write control bits and busy-wait until `ACTIVE`, `FLUSH`, or `RUN` state clears.

State and persistence: DBDMA controller registers and command descriptors are hardware state. The structures encode persistent DMA programs shared with the device.

Dependencies and integration: depends on PowerPC I/O accessors such as `in_le32()` and `out_le32()`. Used by legacy Macintosh device drivers using DBDMA.

Risks and test signals: all fields are little-endian regardless of CPU endian. Busy waits can hang if hardware fails to clear status. Test signals include old PowerMac hardware or emulator boot, DBDMA device transfers, command ring alignment checks, and endian build coverage.
