# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.h

Purpose: Internal core header for the MMIO Analogix DP bridge. It defines state structures, link/video enums, DPCD bit helpers, timeouts, and register-helper prototypes shared between the core and register implementation.

Important APIs/types/functions: Key types are `struct video_info`, `struct link_train`, and `struct analogix_dp_device`. Enums cover lane counts, training states, voltage swing, pre-emphasis, training patterns, color space/depth/coefficient, dynamic range, clock recovery M source, video timing source, analog power blocks, and HPD IRQ types. The prototype set exposes register operations for reset, AUX, HPD, training, video, scrambling, PSR, and transfer.

Control flow: No direct code, but it defines the state machine values consumed by `analogix_dp_core.c`: START, CLOCK_RECOVERY, EQUALIZER_TRAINING, FINISHED, and FAILED. It also defines timeout loop counts that bound HPD, PLL, training, and PSR waits.

State and persistence: `struct analogix_dp_device` is the central in-memory state object. It persists for device lifetime and contains bridge/connector/AUX objects, runtime resources, video settings, link training parameters, PHY, DPMS state, HPD flags, PSR/fast-training booleans, and platform data.

Dependencies and integration: Includes DRM DP helper, CRTC, and bridge headers and forward-declares GPIO. It is private to the Analogix DP implementation and its platform wrappers, not a public UAPI.

Risks: Struct layout and enum values are tightly coupled to register bit encodings. Timeout constants are global policy knobs; too short causes false failures, too long stalls modesets. Callers of register helpers must ensure runtime PM and clock/PHY power are active.

Test signals: Compile coverage across all platform drivers, full link-training state transitions, register-helper API consistency, and suspend/resume build coverage validate this header.
