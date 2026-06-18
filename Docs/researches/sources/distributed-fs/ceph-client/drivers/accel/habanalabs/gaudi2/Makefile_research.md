# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/Makefile

## Purpose

This Makefile contributes the Gaudi2-specific object list for the HabanaLabs accelerator driver build. It is intentionally small: it declares `HL_GAUDI2_FILES` as the three object files that implement Gaudi2 support:

- `gaudi2/gaudi2.o`
- `gaudi2/gaudi2_security.o`
- `gaudi2/gaudi2_coresight.o`

The file is included by `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Makefile`, which appends `$(HL_GAUDI2_FILES)` into `habanalabs-y`. As a result, these Gaudi2 translation units are linked into the single `habanalabs` kernel module whenever `CONFIG_DRM_ACCEL_HABANALABS` builds the driver.

## Important APIs, Types, and Functions

The Makefile itself exposes one build variable:

- `HL_GAUDI2_FILES`: a kbuild-local variable containing the relative object paths for the Gaudi2 implementation.

The objects listed by the variable provide the actual Gaudi2 driver surface:

- `gaudi2/gaudi2.o` is the main chip implementation. It contains Gaudi2 device lifecycle, PCI BAR setup, fixed-property discovery, firmware and CPU initialization, queue manager setup, MMU initialization and invalidation, reset, suspend/resume, command submission parsing, DMA helpers, heartbeat, idle-status checks, event handling, and debug state paths.
- `gaudi2/gaudi2_security.o` provides Gaudi2 protection-bit and range-register setup. It includes unsecured register range tables, LBW/HBW/MMU range programming, security initialization via `gaudi2_init_security()`, protection-bit acknowledgment via `gaudi2_ack_protection_bits_errors()`, and diagnostic printing for protection-bit security errors.
- `gaudi2/gaudi2_coresight.o` provides Gaudi2 CoreSight debug support. It includes component configuration tables, STM/ETF/ETR/funnel/BMON/SPMU programming, CoreSight halt, disabled-component handling, `gaudi2_debug_coresight()`, and `gaudi2_coresight_init()`.

No C APIs, exported symbols, kconfig symbols, build rules, compiler flags, or conditional object clauses are defined directly in this file beyond the object list variable.

## Control Flow

The build control flow is parent-driven:

1. `drivers/accel/habanalabs/Makefile` declares `obj-$(CONFIG_DRM_ACCEL_HABANALABS) := habanalabs.o`.
2. The parent Makefile includes common, Gaudi2, Gaudi, and Goya sub-Makefiles.
3. This file assigns `HL_GAUDI2_FILES`.
4. The parent Makefile appends `$(HL_GAUDI2_FILES)` to `habanalabs-y`.
5. kbuild compiles the listed `.c` files to `.o` files and links them into `habanalabs.o`, then into the built-in object or loadable module according to `CONFIG_DRM_ACCEL_HABANALABS`.

There is no runtime branching in this Makefile. Runtime device matching and chip dispatch are handled by the compiled driver code, while this file only determines that the Gaudi2 implementation is present in the final module.

## State and Persistence Behavior

This file has no runtime state, persistent storage, generated artifacts, or side effects beyond kbuild object selection. Its state is the value of `HL_GAUDI2_FILES` during Makefile evaluation.

The compiled objects it selects do manage hardware and driver state at runtime, including MMU mappings, firmware/CPU state, queue manager state, interrupt state, protection registers, CoreSight debug configuration, DMA memory, and reset/suspend lifecycle state. Those behaviors are not persisted by this Makefile; they are only made available to the module by linking the relevant objects.

## Dependencies

Direct build dependencies:

- Linux kbuild syntax and variable expansion.
- The parent `habanalabs/Makefile`, which includes this file through `include $(src)/gaudi2/Makefile`.
- Source files corresponding to the listed objects:
  - `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2.c`
  - `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_security.c`
  - `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight.c`

Configuration dependencies are inherited from the parent driver:

- `CONFIG_DRM_ACCEL_HABANALABS` controls whether the `habanalabs` driver is built.
- The Kconfig entry depends on `DRM_ACCEL`, `X86 && X86_64`, `PCI`, and `HAS_IOMEM`, and selects support such as `GENERIC_ALLOCATOR`, `HWMON`, `DMA_SHARED_BUFFER`, `CRC32`, and `FW_LOADER`.

The Gaudi2 object list is not gated by a Gaudi2-specific Kconfig symbol. If the parent driver is built, Gaudi2 support is compiled with the rest of the supported HabanaLabs chip families.

## Integration Points

The primary integration point is the parent module aggregation pattern:

- `habanalabs-y += $(HL_COMMON_FILES)`
- `habanalabs-y += $(HL_GAUDI2_FILES)`
- `habanalabs-y += $(HL_GAUDI_FILES)`
- `habanalabs-y += $(HL_GOYA_FILES)`

This file follows the same pattern as the sibling Gaudi and Goya Makefiles, which define `HL_GAUDI_FILES` and `HL_GOYA_FILES`. That symmetry is important for maintainability because the parent Makefile expects each chip-family directory to expose one object-list variable.

At runtime, the selected Gaudi2 objects integrate with the common HabanaLabs framework through shared structures such as `struct hl_device`, common firmware interfaces, PCI helpers, memory management, command submission, IRQ handling, sysfs/hwmon, and user-facing DRM accel IOCTL plumbing. The Makefile does not wire those interfaces directly, but missing or stale entries here would remove whole Gaudi2 feature areas from the linked module.

## Risks

- Missing object risk: adding a new Gaudi2 `.c` file without appending its `.o` here can produce unresolved references, silently omit functionality if no references force linkage, or leave chip support incomplete.
- Stale object risk: leaving a removed or renamed object in `HL_GAUDI2_FILES` causes kbuild failures.
- Unconditional build risk: all Gaudi2 objects are compiled whenever `CONFIG_DRM_ACCEL_HABANALABS` is enabled. Build breaks in Gaudi2 code can affect users who only need another HabanaLabs chip family.
- Ordering risk is low but not zero. kbuild links objects in listed order; most kernel C code should not depend on object order, but initcall/linker-section behavior or duplicate symbols could make ordering observable.
- Scope risk: because this file is only an object list, feature gating, platform filtering, and runtime device matching must be implemented elsewhere. Adding configuration-specific Gaudi2 behavior here would need coordination with parent kbuild and Kconfig.

## Test Signals

Useful signals for validating this file:

- `make` or the repository's kernel build target succeeds with `CONFIG_DRM_ACCEL_HABANALABS=y` and `=m`.
- Build logs show `gaudi2/gaudi2.o`, `gaudi2/gaudi2_security.o`, and `gaudi2/gaudi2_coresight.o` compiled and linked into `habanalabs.o`.
- No unresolved-symbol or missing-object errors appear when Gaudi2 functions such as security initialization or CoreSight debug hooks are referenced from the main Gaudi2 implementation.
- A module build produces a `habanalabs` module that includes Gaudi2 support alongside common, Gaudi, and Goya objects.
- Static checks over the parent Makefile confirm `include $(src)/gaudi2/Makefile` remains paired with `habanalabs-y += $(HL_GAUDI2_FILES)`.
