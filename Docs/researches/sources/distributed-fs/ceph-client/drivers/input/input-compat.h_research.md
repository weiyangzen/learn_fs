# sources/distributed-fs/ceph-client/drivers/input/input-compat.h

`input-compat.h` declares the input subsystem's internal compat ABI helpers and, under `CONFIG_COMPAT`, the 32-bit layout structures they use. `struct input_event_compat` stores 32-bit seconds/useconds plus event type/code/value. `struct ff_periodic_effect_compat` and `struct ff_effect_compat` mirror force-feedback ABI layout with a `compat_uptr_t` custom data pointer.

The header also defines `input_event_size()`, returning `sizeof(struct input_event_compat)` for 32-bit non-time64 compat syscalls and native `sizeof(struct input_event)` otherwise. Evdev uses this to validate read/write chunk sizes and to step through user buffers consistently with conversion helpers. The prototypes expose conversion functions implemented in `input-compat.c`.

There is no runtime state, but this file is a contract boundary for userspace ABI. Dependencies include `linux/compat.h`, `linux/input.h`, and syscall-mode helpers. Risks include structure packing drift, mismatched size decisions relative to conversion functions, and ABI breakage if force-feedback structs evolve without updating compat mirrors. Test signals are compile coverage with and without `CONFIG_COMPAT`, 32-bit evdev event I/O on non-time64 and time64 ABIs, and `EVIOCSFF` struct-size validation.
