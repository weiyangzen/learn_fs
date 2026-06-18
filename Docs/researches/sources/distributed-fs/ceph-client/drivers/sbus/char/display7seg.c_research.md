# sources/distributed-fs/ceph-client/drivers/sbus/char/display7seg.c

Purpose: exposes the Sun CP1400/CP1500 seven-segment display and LED register as a misc character device named `d7s`. It supports ioctl reads/writes/toggle and optional Solaris compatibility behavior.

Important APIs/types/functions: `struct d7s` stores the mapped register and OBP default flipped state. `d7s_open()`, `d7s_release()`, and `d7s_ioctl()` implement the file interface for minor `D7S_MINOR`. `d7s_probe()` maps the one-byte register, registers the misc device, reads `/options/d7s-flipped?`, applies the default flip bit, and stores the singleton `d7s_device`. `d7s_remove()` deregisters and unmaps. The `sol_compat` module parameter controls flip handling.

Control flow: users open `/dev/d7s`, then use `D7SIOCWR` to write the register, `D7SIOCRD` to read it, or `D7SIOCTM` to toggle the flip bit. In non-Solaris mode, the last close restores the OBP flip default. Probe rejects a second device through the global singleton pointer.

State and persistence: state consists of the hardware register byte, global user count, singleton device pointer, module parameter, and stored default flip state. The register controls decimal point, alarm LED, flip bit, and display segment value. No persistent data is written beyond live hardware state.

Dependencies and integration: depends on SPARC OF platform probing for node name `display7seg`, miscdevice registration, `asm/display7seg.h` ioctl/minor definitions, and MMIO byte access.

Risks and test signals: ioctl does not return `-ENOTTY` for unknown commands; it silently returns success with no action. `d7s_remove()` appears to restore the OBP flip state only when `sol_compat` is true, while comments imply non-Solaris mode should honor the default. `of_find_node_by_path("/options")` failure is tolerated. Test singleton probe, register map failure, all three ioctls, unknown ioctl, Solaris and non-Solaris flip behavior on write/close/remove, open count races, and invalid minor handling.
