# sources/distributed-fs/ceph-client/drivers/net/slip/Makefile

Purpose: maps SLIP-related Kconfig symbols to Kbuild objects.

Important build rules: `CONFIG_SLIP` builds `slip.o`; `CONFIG_SLHC` builds `slhc.o`.

Control flow: Kbuild includes the core SLIP network driver when selected and includes Van Jacobsen header compression helpers when `SLHC` is selected directly or via `SLIP_COMPRESSED`. The helper is separate so compression support can be modularized with users that need it.

State and persistence: no runtime state is defined. The file only controls object inclusion.

Dependencies and integration: integrates with `drivers/net/slip/Kconfig` and the parent networking Makefile. `slip.o` consumes exported symbols from `slhc.o` when compressed SLIP support is enabled.

Risks and test signals: risks are unresolved symbols if Kconfig selection and object inclusion diverge, or stale object names after source changes. Test signals include `CONFIG_SLIP=m/y`, `CONFIG_SLIP_COMPRESSED=y` selecting `CONFIG_SLHC`, standalone `SLHC` module builds, and clean modpost output for compressed and uncompressed configurations.
