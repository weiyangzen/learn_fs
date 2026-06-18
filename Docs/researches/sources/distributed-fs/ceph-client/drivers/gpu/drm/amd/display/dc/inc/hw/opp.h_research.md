# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/opp.h

## Purpose

`opp.h` defines the Output Plane Processor abstraction. OPP formats blended pixels for display output, handling formatter setup, clamping, bit-depth reduction, dithering, stereo formatting, display pattern generation, blank colors, ABM-facing state, CRC/debug readout, and the interface between MPC and OPTC.

## Important APIs, Types, And Functions

The header defines clamping ranges and `clamping_and_pixel_encoding_params`, `bit_depth_reduction_params` with truncation, spatial dither, and temporal modulation bitfields, wide-gamut regamma modes, gamma helper structures, hardware adjustment ranges, overlay CSC adjustment items, OPP buffer segmentation, and `dcn_opp_reg_state`. `struct output_pixel_processor` stores context, instance, regamma parameters, MPC tree params, pending MPCC disconnect flags, vtable, and dynamic expansion mode.

`opp_funcs` includes formatter programming, dynamic expansion, bit-depth reduction, underlay adjustment range lookup, destruction, stereo programming, pipe clock control, pattern generator programming, DPG dimension/pending/blank-color handling, left-edge extra pixel setup/readback, and register state readout.

## Control Flow

During stream enablement, resource/hardware sequencing programs OPP format according to color depth and pixel encoding, applies dithering or truncation, configures stereo or test pattern state when needed, and coordinates with MPC/OPTC for pipe connection. DPG operations can blank or generate patterns independent of normal stream data.

## State And Persistence Behavior

OPP software state tracks regamma params, MPC tree parameters, disconnect-pending MPCCs, and dynamic expansion. Hardware state persists in formatter, DPG, ABM, DSC forwarding, CRC, and OPP buffer registers until reprogrammed.

## Dependencies And Integration Points

The header includes `hw_shared.h`, `dc_hw_types.h`, `transform.h`, and `mpc.h`. It integrates with MPC composition, timing generator output, ABM, test-pattern/CTS code, and debug register dumps.

## Risks And Test Signals

Risks include wrong dither depth, clamping range errors, stale disconnect flags, incorrect extra-pixel programming for YCbCr/ODM, and blank/pattern state leaking into normal scanout. Test signals include color-depth modes, DP/HDMI test patterns, stereo modes, CRC captures, ABM-enabled panels, and visual checks for dithering/clamping artifacts.
