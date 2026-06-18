# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/Makefile

## Purpose

This Makefile fragment declares the Goya-specific object files that are linked into the monolithic HabanaLabs kernel module. It is included by `drivers/accel/habanalabs/Makefile`, which appends `$(HL_GOYA_FILES)` to `habanalabs-y` when building `obj-$(CONFIG_DRM_ACCEL_HABANALABS)`.

## Important APIs, types, and data

The only exported build variable is `HL_GOYA_FILES`. It expands to:

- `goya/goya.o`
- `goya/goya_security.o`
- `goya/goya_hwmgr.o`
- `goya/goya_coresight.o`

There are no functions, C types, generated rules, or conditional branches in this fragment. The SPDX tag is `GPL-2.0-only`.

## Control flow

Kbuild reads the parent HabanaLabs Makefile, includes this fragment with `include $(src)/goya/Makefile`, then appends the object list to `habanalabs-y`. The parent file similarly includes common, Gaudi2, and Gaudi fragments, so this file participates in composing one combined `habanalabs.o` module rather than producing a standalone Goya module.

## State and persistence behavior

The fragment has no runtime state and no generated artifacts on its own. Its build-state effect is deterministic: if the parent Makefile is evaluated, the four listed Goya objects become part of the module link. Incremental build systems will track the resulting object dependencies through normal Kbuild mechanisms.

## Dependencies and integration points

The fragment depends on the existence and successful compilation of the four corresponding source files under `drivers/accel/habanalabs/goya/`. The parent Makefile supplies the inclusion context and the final `habanalabs-y += $(HL_GOYA_FILES)` append. The object list makes Goya security, hardware-manager, coresight, and main device logic available to the shared driver.

## Risks and edge cases

Because this is an unconditional object list, removing or renaming any listed source file breaks the HabanaLabs module build even on systems that do not instantiate Goya hardware. Conversely, adding a new Goya source file without updating this variable leaves code unlinked and can surface later as missing symbols or absent functionality.

The double space after `:=` is harmless to make. The trailing backslash on the first assignment line is required; deleting it would drop `goya/goya_coresight.o` from the variable or produce a parse issue depending on the edit.

## Test signals

The primary validation is a kernel/module build with `CONFIG_DRM_ACCEL_HABANALABS` enabled. A dependency audit should confirm that all four object paths have matching source files and that no Goya-only object with referenced symbols is omitted from `HL_GOYA_FILES`.
