# sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.h

Purpose: Private interface and register definition header for the Alvium CSI-2 driver. It defines the BCRM and GenCP register addresses, feature bit layouts, supported MIPI/Bayer format enums, per-mode structures, control bookkeeping, and the main `struct alvium_dev` state used by `alvium-csi2.c`.

Important APIs/types/functions: `REG_BCRM_V4L2_*()` macros tag BCRM-relative CCI register definitions so the source file can add the runtime-discovered BCRM base address. Register constants cover BCRM versioning, firmware, handshake, CSI-2 lane/clock setup, acquisition start/stop/frame rate, image geometry, MIPI data type, Bayer pattern, flip controls, exposure/gain/white-balance/color controls, temperature, heartbeat, and GenCP mode switching. Key types are `enum alvium_bcrm_mode`, `enum alvium_mipi_fmt`, `enum alvium_av_bayer_bit`, `enum alvium_av_mipi_bit`, `struct alvium_avail_feat`, `struct alvium_avail_mipi_fmt`, `struct alvium_avail_bayer`, `struct alvium_mode`, `struct alvium_pixfmt`, `struct alvium_ctrls`, and `struct alvium_dev`.

Control flow: The header has no executable control flow, but it encodes how the source driver is organized: read feature inquiry into bitfield structures, map available MIPI/Bayer bits to `struct alvium_pixfmt`, store discovered min/max/inc defaults in `struct alvium_dev`, then expose those through V4L2 controls and pad operations.

State/persistence: `struct alvium_dev` is the persistent in-kernel cache of camera hardware state: BCRM address, endpoint configuration, regulator, regmap, capability flags, geometry/control ranges, active/default mode, link frequency, V4L2 control pointers, current BCRM mode, allocated format table, streaming flag, and frame-interval apply flag.

Dependencies/integration: Includes Linux kernel, regulator, V4L2 CCI, V4L2 common/control/fwnode/subdev headers. It is not a public UAPI header; it is tightly coupled to the source file and the Alvium BCRM firmware contract.

Risks: The `struct alvium_avail_*` bitfields are used over raw register values; bit order assumptions are fragile across endianness/compiler layout. Some register names mix units and access semantics, so source-side mistakes can silently target the wrong BCRM register. Range fields use a mix of `u32`, `u64`, and `s32`, requiring careful casts from CCI reads.

Test signals: Build coverage should catch missing types and macro changes. Runtime tests should verify that each BCRM register macro resolves correctly after `bcrm_addr` relocation and that feature bit decoding matches actual camera-reported capabilities.
