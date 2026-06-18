# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_frontend.h

## Purpose
`sun4i_frontend.h` defines the register map, variant data, state structure, exported symbols, and helper API for the Allwinner frontend scaler/CSC block.

## Important APIs, Types, and Functions
- Register macros for enable, frame control, bypass, buffer addresses, tiled offsets, line stride, input/output formats, CSC coefficients, input/output sizes, scaling factors, phases, and FIR coefficient tables.
- `struct sun4i_frontend_data`: per-compatible flags for coefficient access/ready behavior and phase values.
- `struct sun4i_frontend`: component state with list node, device/node, clocks, regmap, reset, and variant data.
- Exported helpers for init/exit/enable, buffer/coord/format programming, format support, OF match table, and `sunxi_bt601_yuv2rgb_coef`.

## Control Flow, State, and Persistence
The header declares the state used by `sun4i_frontend.c` and the API called from backend/layer paths. Register macros define how plane state is translated into frontend hardware programming.

## Dependencies and Integration Points
It depends on list and OF match declarations, forward declarations for DRM plane/regmap/reset/clock types, and is consumed by `sun4i_backend.c`, `sun4i_drv.c`, and frontend implementation.

## Risks and Test Signals
Risks include incorrect register bit definitions, fixed assumptions about two scaler channels and three buffer planes, and exported API drift. Tests should build all users, validate register writes for representative formats, and ensure Kconfig/module combinations resolve exported symbols correctly.
