<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h

Purpose: Declares Aspeed GPIO coproccessor coordination helpers for GPIO lines shared with a coproccessor.

Important APIs/types/functions: `aspeed_gpio_copro_ops` provides `request_access()` and `release_access()` callbacks. APIs include `aspeed_gpio_copro_grab_gpio()` to claim a descriptor and return value/data register offsets plus bit, `aspeed_gpio_copro_release_gpio()`, and `aspeed_gpio_copro_set_ops()` to install copro access callbacks and private data.

Control flow: A copro-aware user installs access ops, grabs a GPIO descriptor to obtain hardware register coordinates, performs coordinated access, then releases it.

State and persistence behavior: Runtime state is maintained by the Aspeed GPIO implementation, including registered ops and any claimed line ownership. Hardware register offsets identify persistent controller registers, not stored by the header.

Dependencies and integration points: Depends on GPIO descriptors and Aspeed GPIO controller internals. Integrates BMC host/coprocessor coordination with gpiolib.

Risks: Incorrect grab/release pairing can leave GPIO access blocked. Register offsets and bit values must match controller generation. Access callbacks may need strict locking against host GPIO operations.

Test signals: Aspeed GPIO build tests, grab/release lifecycle tests, concurrent host/copro access, invalid descriptor handling, and hardware register offset validation on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h -->
