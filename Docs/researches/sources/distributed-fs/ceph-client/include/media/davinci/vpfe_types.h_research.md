# sources/distributed-fs/ceph-client/include/media/davinci/vpfe_types.h

Purpose: Platform-data definitions for TI DaVinci VPFE capture hardware interface wiring.

Important APIs/types/functions: `enum vpfe_pin_pol` encodes positive/negative signal polarity. `enum vpfe_hw_if_type` describes BT.656, BT.1120, raw Bayer, external-sync YCbCr 8/16-bit, and 10-bit BT.656. `struct vpfe_hw_if_param` groups interface type with horizontal and vertical polarity.

Control flow: Board/platform code fills `vpfe_hw_if_param`; the capture driver consumes it when configuring VPFE input timing and bus mode.

State and persistence: No runtime state. It is compile-time/platform configuration, guarded by `__KERNEL__`.

Dependencies and integration: Integrates old board-file style DaVinci media drivers with VPFE host configuration.

Risks and test signals: Risks are wrong polarity or bus-type selection producing unstable capture. Test each board mode with known video sources, sync polarity combinations, and raw/YCbCr bus formats.
