# sources/distributed-fs/ceph-client/arch/m68k/apollo/apollo.h

Purpose: local Apollo interrupt initialization declaration.

The sole API is `void dn_init_IRQ(void);`, implemented in `dn_ints.c` and called by `config_apollo()` through `mach_init_IRQ`.

State: none. The declared function installs IRQ controller state elsewhere.

Dependencies and integration are local to the Apollo machine directory and m68k machdep hook setup.

Risks and test signals: prototype mismatch is compile-time visible. Runtime validation is successful Apollo IRQ setup and timer interrupt delivery.
