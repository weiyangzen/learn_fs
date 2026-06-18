# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.h

## Purpose
This header is the Tonga-family BACO interface declaration for the legacy PowerPlay hardware-manager layer. It includes `smu7_baco.h` so callers share the SMU7 BACO state definitions and command helpers, and it exposes one ASIC-specific transition function, `tonga_baco_set_state()`.

## Important APIs, Types, and Functions
- `tonga_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: public entry point for placing a Tonga ASIC into or out of BACO. The implementation lives outside this header and is expected to use `struct pp_hwmgr` as the device power-management context.
- `enum BACO_STATE`: imported from `smu7_baco.h`; callers pass the target BACO state rather than manipulating register scripts directly.

## Control Flow and Integration
The file has no runtime control flow. Its role is compile-time integration: it lets Tonga-specific hardware-manager code register or call the BACO transition implementation while reusing the SMU7 BACO contract. It mirrors the Vega10 header pattern in this subset, but points at SMU7 rather than SMU9.

## State and Persistence
No state is stored here. State is external in the `pp_hwmgr` backend, the BACO state machine, and the hardware registers touched by the implementation.

## Dependencies
- `smu7_baco.h` for `enum BACO_STATE` and likely the lower-level BACO register-programming support.
- PowerPlay hardware-manager definitions through the included SMU7 BACO header.

## Risks
- The header assumes the implementation and `smu7_baco.h` agree on `enum BACO_STATE` semantics. A mismatch would break suspend, runtime power-management, or passthrough BACO transitions.
- Because only an extern is declared, compile/link coverage is the main guard against missing implementation.

## Test Signals
- Kernel build/link tests should verify that users of `tonga_baco_set_state()` resolve correctly.
- Runtime BACO tests should exercise both `BACO_STATE_IN` and `BACO_STATE_OUT` on supported Tonga hardware, checking that the current BACO state matches the requested state and that device resume remains functional.
