# sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Makefile

Purpose: this Kbuild file maps the Adaptec Starfire Kconfig symbol to its object file.

Important APIs, types, and functions: the build rule is `obj-$(CONFIG_ADAPTEC_STARFIRE) += starfire.o`.

Control flow: when the parent Ethernet Makefile descends into `adaptec/`, Kbuild builds `starfire.o` built-in for `CONFIG_ADAPTEC_STARFIRE=y`, as a module for `m`, or not at all when disabled.

State and persistence: no runtime state. Build products are derived from `.config`.

Dependencies and integration points: depends on `adaptec/Kconfig` defining `CONFIG_ADAPTEC_STARFIRE` and on `starfire.c` existing in this directory. It integrates with module metadata in the C file and parent vendor-directory selection through `CONFIG_NET_VENDOR_ADAPTEC`.

Risks: a symbol rename or file rename without this line update would silently disable the driver build. Additional source files for Starfire would require a composite-object rule.

Test signals: targeted Kbuild with `CONFIG_NET_VENDOR_ADAPTEC=y` and `CONFIG_ADAPTEC_STARFIRE=m/y`, verifying `starfire.o` or `starfire.ko` is generated without missing-object errors.
