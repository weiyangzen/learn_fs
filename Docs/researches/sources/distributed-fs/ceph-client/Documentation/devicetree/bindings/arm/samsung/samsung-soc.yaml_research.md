<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml

## Purpose
This schema validates Samsung SoC root-compatible fallback strings independent of specific boards.

## Important APIs, Types, And Functions
It fixes the root node to `/` and allows SoC-level compatibles including `samsung,s3c2416`, `s3c2440`, `s3c6410`, `s5pv210`, and multiple Exynos SoCs from Exynos3250 through ExynosAutoV920.

## Control Flow
The `compatible` property is an enum, so validation accepts one SoC string rather than a board fallback chain.

## State And Persistence
It records immutable SoC identity only.

## Dependencies And Integration Points
It complements `samsung-boards.yaml` and integrates with SoC-level DTS/platform matching.

## Risks
Board DTS files usually need board-level compatibles; using only a SoC enum loses board-specific identity. New SoCs require explicit enum additions.

## Test Signals
`dtbs_check` validates SoC root compatibles; platform boot confirms SoC-level matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml -->
