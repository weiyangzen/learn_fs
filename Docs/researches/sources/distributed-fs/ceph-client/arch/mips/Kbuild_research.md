# sources/distributed-fs/ceph-client/arch/mips/Kbuild

Purpose: top-level Kbuild composition for the MIPS architecture subtree.

Important build rules and state: includes `arch/mips/Kbuild.platforms`, assigns `obj-y` and `obj-` from `platform-y`, then adds generic architecture directories `generic/`, `kernel/`, `mm/`, `net/`, and `vdso/`; adds `kvm/` under `CONFIG_KVM`; includes `boot` as a clean subdir.

Control flow: build-time only. The `obj- := $(platform-y)` line exists so make clean traverses platform objects before `.config` has been included.

State and persistence: determines linked MIPS architecture object directories and clean traversal.

Dependencies and integration: consumed by top-level Kbuild for MIPS builds; depends on platform definitions from `Kbuild.platforms`.

Risks and test signals: directory ordering affects link composition. Missing `obj-` clean behavior can leave platform artifacts. Test MIPS allnoconfig/defconfig builds, KVM on/off, and `make ARCH=mips clean`.
