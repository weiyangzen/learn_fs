# sources/distributed-fs/ceph-client/arch/x86/boot/io.h

Purpose: defines boot-time port I/O indirection so normal x86 I/O instructions can be replaced in TDX guests.

Important APIs and state: `struct port_io_ops` holds `f_inb`, `f_outb`, and `f_outw`; external `pio_ops` stores active callbacks. `init_default_io_ops()` installs `__inb`, `__outb`, and `__outw`. Macros redefine `inb`, `outb`, and `outw` to call through `pio_ops`.

Control flow: callers initialize defaults early, then TDX detection may override callbacks.

Dependencies and integration: included by setup and compressed code that uses port I/O, including serial, PIC masking, VGA, and TDX paths.

Risks and test signals: code using `inw/inl/outl` is not redirected here. Missing `init_default_io_ops()` leaves null callbacks. Test non-TDX boot for default callbacks and TDX boot for hypercall callbacks before first sensitive I/O.
