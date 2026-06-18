# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/Makefile

## Purpose

This short Makefile wires common arm64 KVM hyp objects into the kernel build and propagates the hyp include directory to C and assembly subdirectories.

## Important APIs, Types, And Functions

It sets `incdir := $(src)/include`, adds `-I$(incdir)` through `subdir-asflags-y` and `subdir-ccflags-y`, and includes `vhe/`, `nvhe/`, and `pgtable.o` when `CONFIG_KVM` is enabled.

## Control Flow

There is no runtime control flow. Build-time control is Kconfig-gated through `obj-$(CONFIG_KVM)`.

## State And Persistence Behavior

The file persists build configuration only. It does not create runtime state.

## Dependencies And Integration Points

It is the parent build entry for VHE, nVHE, and shared hyp page-table code. The include path is required by headers such as `hyp/switch.h`, `hyp/fault.h`, and nVHE private headers.

## Risks And Test Signals

Risks are missing include paths or accidentally excluding VHE/nVHE objects. Test signals are successful `CONFIG_KVM=y/m` arm64 builds and expected object inclusion for shared `pgtable.o`.
