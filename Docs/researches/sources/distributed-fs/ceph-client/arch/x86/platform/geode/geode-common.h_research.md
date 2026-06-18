<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h

## Purpose
Declares the shared API used by Geode board-specific setup files to create GPIO LEDs and restart keys.

## Important APIs, Types, And Functions
`struct geode_led` carries a GPIO pin and default-on flag. `geode_create_restart_key()` and `geode_create_leds()` are exported to sibling compilation units.

## Control Flow
The header has no runtime flow; it defines the compile-time contract between board detectors and `geode-common.c`.

## State And Persistence
No state is stored in the header. Callers pass static `__initconst` LED arrays.

## Dependencies And Integration Points
Includes Linux property definitions and is included by ALIX, GEOS, net5501, and the common implementation.

## Risks And Edge Cases
Signature drift between declarations and implementation would break builds. The small API deliberately hides software-node details from board files.

## Test Signals
Successful compilation of all Geode board objects is the direct validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h -->
