# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/ipp.h

## Purpose

`ipp.h` defines the input pixel processor abstraction used by older DC hardware paths. IPP handles cursor programming, input format expansion/conversion, prescale, input LUT programming, and degamma setup before pixels move further into the display pipeline.

## Important APIs, Types, And Functions

`struct input_pixel_processor` stores the DC context, hardware instance, and `ipp_funcs` vtable. `enum ipp_prescale_mode` and `struct ipp_prescale_params` describe signed/unsigned fixed or float prescale programming. `enum ovl_color_space` provides overlay color-space selectors. The `ipp_funcs` table includes cursor position/attribute programming, full bypass, generic IPP setup, DCE-specific prescale, input LUT programming, degamma mode selection, degamma PWL programming, and destruction.

## Control Flow

The header defines a classic hardware object pattern: resource construction creates an IPP object, assigns an ASIC-specific vtable, and higher layers call through `ipp->funcs`. Typical setup moves from cursor updates and input-format setup to optional LUT/degamma programming. `ipp_full_bypass` is the escape path for disabling processing.

## State And Persistence Behavior

The IPP object persists as part of the resource pool. Runtime state lives in hardware registers and in the chosen function table, not in this header. Programming cursor attributes, LUTs, and degamma settings persists until the pipe is reprogrammed, disabled, or reset.

## Dependencies And Integration Points

The file depends on `hw_shared.h` and `dc_hw_types.h` for pixel format, expansion, color matrix, cursor, and PWL structures. It integrates with transform/DPP-era code because `transform.h` exposes compatible IPP function hooks while newer hardware folds IPP behavior into DPP/transform blocks.

## Risks And Test Signals

Main risks are NULL vtable slots on ASICs that do not implement a feature, mismatched PWL data, and incorrect bypass/setup ordering during modeset. Test signals include cursor movement/format validation, input LUT and degamma IGT or color tests, plane format conversion checks, and suspend/resume or hotplug modesets that reapply IPP state.
