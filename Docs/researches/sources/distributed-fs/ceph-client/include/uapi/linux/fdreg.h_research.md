# sources/distributed-fs/ceph-client/include/uapi/linux/fdreg.h

This UAPI header provides low-level floppy disk controller register offsets, command bits, status bits, and controller result codes. It is used by floppy driver code and low-level diagnostic utilities that need symbolic names for FDC programming.

Important exports include register offsets such as `FD_SRA`, `FD_SRB`, `FD_DOR`, `FD_TDR`, `FD_DSR`, `FD_STATUS`, `FD_DATA`, `FD_DIR`, `FD_DCR`, digital output bits like motor and DMA/IRQ enable masks, main status bits, command opcodes for read/write/format/seek/recalibrate/sense/configure, and status register result bits for abnormal termination, write protect, no data, CRC, missing address marks, and seek/equipment errors.

Control flow is hardware-protocol oriented: the floppy driver writes commands and parameters to the data register, watches main/status registers, waits for IRQ/DMA completion, then reads result bytes and updates drive state. The header has no state itself; state is in the physical FDC, drive motors, media, IRQ/DMA engine, and driver bookkeeping.

Dependencies are the IBM PC-compatible floppy controller programming model and the Linux floppy driver. Integration points include `fd.h` raw commands, architecture I/O port helpers, and legacy hardware emulators.

Risks are incorrect bit definitions causing controller hangs, emulator/hardware variation, command/result byte ordering mistakes, and accidental exposure of hardware-level controls to untrusted users. Test signals include floppy hardware or QEMU regression tests, command/status decode tests, raw command ioctl coverage, and compile checks for driver constants.
