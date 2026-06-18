# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-tpg.c

Purpose: Implements the Mali-C55 internal test pattern generator subdevice used as a camera-like source when no external sensor is required or available.

Important APIs/functions: Exports `mali_c55_register_tpg()` and unregister helper. Internal code manages supported mbus codes, frame-size/format negotiation, V4L2 controls for test pattern, hblank, vblank, and pixel rate, stream enable/disable, TPG register configuration, and default bright background programming.

Control flow: Set-format clamps dimensions and supported codes, then updates vblank defaults/ranges for active formats. Controls write TPG pattern and vertical blanking only if runtime PM is active. Stream enable configures fixed hblank, multi-frame generator mode, raw/RGB pattern format, applies controls, enables pattern generation in context registers, and turns on generated video globally. Stream disable clears those bits.

State and persistence: TPG state stores subdev, single source pad, control handler, vblank control pointer, and owning `mali_c55`. Active format lives in subdev state; control values persist in the V4L2 control framework.

Dependencies and integration: Uses V4L2 subdev and control APIs, PM runtime, core/context register helpers, and ISP sink links.

Risks: The fixed pixel rate and vblank heuristic assume hardware timing that should be validated across formats. Control writes are skipped when device is suspended and rely on later handler setup at stream enable. TPG entity function is camera sensor, so graph users must distinguish it from external sensors.

Test signals: TPG-only streaming, test pattern menu changes, vblank range recalculation for min/max frame sizes, raw/RGB format propagation to ISP, suspend/resume plus control restore, and media link switching between TPG and external sensor.
