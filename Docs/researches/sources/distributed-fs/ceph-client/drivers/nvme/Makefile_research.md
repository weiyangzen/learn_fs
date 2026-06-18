# sources/distributed-fs/ceph-client/drivers/nvme/Makefile

Purpose: Adds NVMe common, host, and target subdirectories to the kernel build.

Important APIs and flow: Unconditionally appends `common/`, `host/`, and `target/` to `obj-y`; each subdirectory decides which objects are built through its own Kconfig-controlled Makefile.

State and persistence behavior: No runtime state. It is build-system wiring only.

Dependencies and integration points: Integrates with kbuild recursion and the subdirectory Makefiles for common authentication/keyring code, host transports, and target transports.

Risks and test signals: Build tests should verify empty/unselected subtrees remain harmless and selected modules get linked from the proper subdirectory.
