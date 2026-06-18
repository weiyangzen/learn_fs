# sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.h

## Purpose
`msp3400-driver.h` is the shared internal header for the MSP34xx TV sound processor driver. It defines mode/routing constants, module-parameter externs, the driver-private `struct msp_state`, helper accessors, and cross-file function prototypes used by `msp3400-driver.c` and `msp3400-kthreads.c`.

## Important APIs, Types, and Functions
- `MSP_CARRIER(freq)` converts an audio carrier frequency into the fixed-point carrier value expected by MSP demodulator registers.
- `MSP_MODE_*` constants enumerate demodulator/DSP modes: AM detect, FM radio, terrestrial FM, satellite FM, NICAM variants, BTSC, and external input.
- `SCART_*` constants encode SCART inputs and outputs used by the ACB switch matrix.
- `OPMODE_*` constants select manual, autodetect, or autoselect operation.
- `enum msp3400_pads` defines optional media-controller audio sink/source pads.
- `struct msp_state` stores all persistent driver state: subdev/control handler, revision IDs, feature flags, runtime audio/radio/standard/mode/carrier/routing state, V4L2 audio controls, scan flags, kthread/wait-queue control, and optional media pads.
- `to_state()` and `ctrl_to_state()` recover `struct msp_state` from a subdev or control.
- Prototypes expose low-level DSP/DEM access, reset, SCART switching, volume update, sleep/wake-thread helpers, standard naming/detection helpers, kthread entry points, and manual-mode programming helpers.

## Control Flow
The header does not execute control flow directly, but it defines the data and call surface that binds the main driver and the kthread implementation. The main driver owns allocation, probe/remove, V4L2 callbacks, and control setup. The kthread file owns carrier-detection/autoselect loops and calls the public low-level helpers declared here.

## State and Persistence Behavior
`struct msp_state` is the persistent state object attached to the V4L2 subdev/I2C client. It is shared by synchronous ioctl/control callbacks and asynchronous kthreads. Route, mode, standard, and audio fields mirror both requested software state and programmed hardware state. The restart/watch bits and wait queue are the thread-control mechanism.

## Dependencies and Integration Points
The header depends on V4L2 device/control/media-controller headers and `<media/drv-intf/msp3400.h>` for external routing constants. It is included by both MSP source files, so any change to `struct msp_state` or prototypes affects the whole MSP driver.

## Risks and Edge Cases
- `MSP_CARRIER()` uses floating-point syntax in a macro intended for constants only, relying on compile-time folding. Using it with non-constant values would violate kernel floating-point rules.
- `struct msp_state` exposes many mutable fields without lock annotations, making it easy to add racy call paths.
- The header prototypes create tight coupling between main driver and kthread internals; changing opmode behavior needs coordinated updates in both files.
- Feature flags are compact `u8` booleans; new features should keep semantics clear to avoid confusing capability-derived code paths.

## Test Signals
- Compile with media-controller enabled and disabled to validate the conditional pad member.
- Validate all prototypes match definitions in `msp3400-driver.c` and `msp3400-kthreads.c`.
- Static analysis should check shared state use across kthread and V4L2 callbacks.
- Unit-style checks for `MSP_CARRIER()` should use only literal constants and verify known carrier register values.
