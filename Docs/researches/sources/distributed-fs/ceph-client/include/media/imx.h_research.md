# sources/distributed-fs/ceph-client/include/media/imx.h

## Purpose
Provides a thin shared include point for i.MX media drivers.

## Important APIs, Types, and Functions
The header contains an include guard and includes `<linux/imx-media.h>`, re-exporting the platform i.MX media definitions to media drivers.

## Control Flow
No executable flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by i.MX media source files that include the media-layer header while relying on Linux i.MX media definitions.

## Risks
Because it is a wrapper, risk is mainly include-order churn or divergence from `<linux/imx-media.h>`.

## Test Signals
Compile coverage for i.MX media drivers and include-order checks with `<linux/imx-media.h>`.
