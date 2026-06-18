# sources/distributed-fs/ceph-client/include/uapi/linux/fd.h

This header defines the legacy floppy disk userspace ABI for geometry, formatting, error thresholds, drive parameters, drive/FDC status, write-error logging, raw controller commands, and eject/reset operations.

Important exports include `struct floppy_struct`, `struct format_descr`, `struct floppy_max_errors`, `floppy_drive_name`, `struct floppy_drive_params`, `struct floppy_drive_struct`, `enum reset_mode`, `struct floppy_fdc_state`, `struct floppy_write_errors`, and `struct floppy_raw_cmd`. Ioctls include `FDCLRPRM`, `FDSETPRM`, `FDDEFPRM`, `FDGETPRM`, `FDMSGON`, `FDMSGOFF`, format commands `FDFMTBEG/TRK/END`, `FDFLUSH`, `FDSETMAXERRS`, `FDGETMAXERRS`, `FDGETDRVTYP`, `FDSETDRVPRM`, `FDGETDRVPRM`, `FDGETDRVSTAT`, `FDPOLLDRVSTAT`, `FDRESET`, `FDGETFDCSTAT`, `FDWERRORCLR`, `FDWERRORGET`, `FDRAWCMD`, `FDTWADDLE`, and `FDEJECT`.

Control flow is device ioctl based on `/dev/fd*`: userspace configures media geometry, optionally formats tracks, queries drive/controller state, sends raw FDC commands, or resets/ejects media. State lives in the floppy driver, drive motor and head position, cached geometry, media-change generation, controller registers, DMA buffers, and write-error accounting. Persistent behavior is physical media formatting and written data; most parameters are driver runtime state.

Dependencies include `linux/ioctl.h`, `linux/compiler.h`, the floppy block driver, FDC hardware, DMA/IRQ plumbing, and architecture I/O port access. Integration points are fdutils, old installers/recovery tools, and block-device stack compatibility.

Risks include pointer fields and chained raw commands in UAPI structs, privilege requirements for destructive commands, stale media-change detection, timing-sensitive hardware behavior, 32-bit compat layout problems, and the potential for raw commands to wedge controllers. Test signals include floppy driver ioctl tests where hardware/emulation exists, QEMU floppy tests, raw-command validation, format/readback tests, media-change polling tests, and compile/compat layout checks.
