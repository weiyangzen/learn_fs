<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h

## Purpose
This header defines output type constants for PCA955x LED/GPIO expander bindings.

## Important APIs, types, and functions
It exports `PCA955X_TYPE_NONE`, `PCA955X_TYPE_LED`, and `PCA955X_TYPE_GPIO`.

## Control flow
DTS child nodes reference these constants to describe output usage. The PCA955x driver uses the numeric type to register LEDs, GPIOs, or leave outputs unused.

## State and persistence
The header is stateless. The board's selected types persist in the DTB and determine runtime registration.

## Dependencies and integration points
It integrates with PCA955x I2C LED controller support, LED class registration, GPIO subsystem exposure, and board schemas.

## Risks and test signals
Risks include wrong LED/GPIO classification, creating userspace ABI differences, or driving pins unexpectedly. Test signals include `dtbs_check`, I2C probe, LED class entries, GPIO line toggling, and output electrical validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h -->
