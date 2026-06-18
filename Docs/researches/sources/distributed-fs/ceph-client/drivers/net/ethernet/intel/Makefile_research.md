## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/Makefile

Purpose: Kbuild dispatcher for Intel Ethernet drivers. It maps Intel-related `CONFIG_*` symbols from `Kconfig` to the library directories, object files, and driver subdirectories that should be built.

Important APIs, types, and functions: the file uses Kbuild `obj-$(CONFIG_...) += ...` and `obj-y += ...` assignments. `CONFIG_LIBETH` gates `libeth/`; `libie/` is always descended into through `obj-y`; driver symbols select `e100.o`, `e1000/`, `e1000e/`, `igb/`, `igc/`, `igbvf/`, `ixgbe/`, `ixgbevf/`, `i40e/`, `iavf/`, `fm10k/`, `ice/`, and `idpf/`.

Control flow: parent network Kbuild enters this directory when Intel Ethernet support is in scope. Kbuild evaluates each object line against the final `.config`; enabled built-in symbols add directories or objects to built-in traversal, module symbols add module build targets, and disabled symbols omit them. `libie/` is always traversed, while `libeth/` is conditional on `CONFIG_LIBETH`.

State and persistence behavior: there is no runtime state. Build state is derived from `.config`, and the outputs persist as built-in objects or loadable modules in the kernel build tree. The unconditional `libie/` line means its subdirectory Makefile must be safe when consumers are disabled.

Dependencies and integration points: this Makefile is paired with `drivers/net/ethernet/intel/Kconfig`; symbol names must remain synchronized. It integrates with subdirectory Makefiles for multi-object drivers and with the parent `drivers/net/ethernet/Makefile`. The `CONFIG_IAVF` object rule intentionally builds `iavf/`, matching Kconfig's hidden `IAVF` symbol selected by legacy `I40EVF`.

Risks and edge cases: symbol drift between Kconfig and Makefile will produce drivers that can be configured but not built, or directories that are built without a user-visible symbol. Unconditional library traversal can expose latent build errors if subdirectory Makefiles do not guard their objects. Ordering of common libraries before consumers is useful for clarity, though Kbuild dependency resolution handles most link ordering.

Test signals: enable each Intel driver symbol as `m` and `y` in targeted build fragments and verify the expected object or subdirectory appears in the build. Check that `CONFIG_I40EVF=m` results in `CONFIG_IAVF=m` and builds `iavf/`, that `CONFIG_LIBETH` controls `libeth/`, and that disabling all Intel drivers still allows the unconditional `libie/` traversal to complete without building unwanted driver modules.
