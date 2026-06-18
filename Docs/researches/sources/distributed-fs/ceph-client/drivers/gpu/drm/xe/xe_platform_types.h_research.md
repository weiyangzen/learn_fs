<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h

## Purpose

`xe_platform_types.h` defines the canonical Xe platform and subplatform enums used throughout the driver.

## Important APIs and Types

`enum xe_platform` names platform families in graphics-version and chronological order, starting at `XE_PLATFORM_UNINITIALIZED` and covering Tigerlake, Rocketlake, Alder/Raptor Lake variants, DG1/DG2/PVC, Meteor/Lunar/Battlemage/Pantherlake, Novalake, Crescent Island, and Novalake-P. `enum xe_subplatform` identifies finer PCI-ID-derived variants such as RPLU, RPLS, DG2 G10/G11/G12, and BMG G21.

## Control Flow and State

The header has no runtime logic. PCI probe fills `xe->info.platform` and `xe->info.subplatform`; later code uses those enum values for workarounds, PAT tables, PM policy, display behavior, and feature gating.

## Dependencies and Integration Points

It is included by PCI descriptor types and many platform-checking helpers. The enum order is documented as intentional and should be maintained for readability and stable platform classification.

## Risks and Test Signals

Adding or reordering platforms can break switch statements, platform macros, descriptor tables, and tests that assume chronological order. Test signals include build coverage for exhaustive platform switches, PCI descriptor mapping for each enum, and feature/workaround selection for new platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_platform_types.h -->
