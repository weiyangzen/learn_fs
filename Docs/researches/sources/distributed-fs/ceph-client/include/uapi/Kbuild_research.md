# sources/distributed-fs/ceph-client/include/uapi/Kbuild

Purpose: Controls top-level UAPI header export exclusions for architecture-dependent Linux headers.

Important APIs/types/functions: Uses `no-export-headers += linux/a.out.h`, `linux/kvm.h`, and `linux/kvm_para.h` when the corresponding architecture UAPI or generated UAPI asm headers are absent.

Control flow: During headers install, Kbuild evaluates `wildcard` checks against `$(srctree)` and `$(objtree)` for `$(SRCARCH)` and appends headers that must not be exported.

State/persistence: No runtime state; it influences generated/install header trees.

Dependencies/integration: Integrated with kernel headers-install machinery and architecture include directories.

Risks: Wrong wildcard logic can export unusable UAPI headers or hide valid ones for an architecture.

Test signals: Run `make headers_install` for architectures with and without KVM/a.out support and verify exported header set.
