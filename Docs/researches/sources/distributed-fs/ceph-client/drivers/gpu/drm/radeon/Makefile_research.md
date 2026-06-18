# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Makefile

Purpose: This Makefile defines how the Radeon DRM driver and its generated register-safety headers are built.

Important APIs, types, and functions: It builds host tool `mkregtable`, generates `*_reg_safe.h` files from `reg_srcs/%`, declares per-object dependencies on generated headers, and composes `radeon-y` from core, ASIC, KMS, memory, command submission, display, power-management, audio, DMA, UVD, VCE, VM, and optional ACPI/VGA switcheroo objects.

Control flow: Kbuild first builds `mkregtable`, generates register safe-list headers through `if_changed,mkregtable`, then compiles object files that depend on those headers. `obj-$(CONFIG_DRM_RADEON) += radeon.o` links the aggregate module/built-in.

State and persistence: No runtime state. Generated headers persist in the build output tree and affect command submission/register validation code.

Dependencies and integration points: Tied to Radeon Kconfig, Kbuild host programs, generated register source files, and all Radeon subsystem translation units. Optional objects are gated by `CONFIG_MMU_NOTIFIER`, `CONFIG_VGA_SWITCHEROO`, and `CONFIG_ACPI`.

Risks: Missing generated-header dependencies can cause stale or absent register safety tables. The large object list must stay synchronized with source files and feature config. Host tool failures break builds before driver compilation.

Test signals: Clean and incremental builds; touch `reg_srcs/*` and confirm regeneration; build with optional configs toggled; verify `radeon.o` contains expected ASIC/power/video/audio objects.
