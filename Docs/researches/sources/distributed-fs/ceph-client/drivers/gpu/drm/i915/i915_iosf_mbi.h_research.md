# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_iosf_mbi.h

## Purpose
Provides an architecture/configuration abstraction for IOSF MBI access used by i915, allowing the driver to compile on non-x86 or non-IOSF configurations.

## Important APIs, types, and functions
Includes `<asm/iosf_mbi.h>` when `CONFIG_IOSF_MBI` is enabled. Otherwise defines PMIC bus access event constants, forward declares `struct notifier_block`, and supplies empty or success-returning stubs for punit acquire/release/assert and PMIC notifier registration.

## Control flow
Compile-time configuration chooses real IOSF functions or stubs.

## State and persistence
The stub path stores no state and never serializes real hardware access.

## Dependencies and integration points
Used by i915 code that needs IOSF/PUnit/PMIC coordination without making the whole driver x86-only.

## Risks
On platforms that genuinely need IOSF coordination, building without `CONFIG_IOSF_MBI` would make calls no-ops. This is expected only for unsupported/non-x86 paths where the hardware access is not meaningful.

## Test signals
Compile on x86 with IOSF enabled and on non-x86/allmodconfig-style builds without IOSF. Runtime PMIC/PUnit notifier behavior belongs to real IOSF configurations.
