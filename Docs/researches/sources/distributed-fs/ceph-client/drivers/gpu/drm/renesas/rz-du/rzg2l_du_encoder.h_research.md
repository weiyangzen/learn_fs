# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.h

## Purpose

`rzg2l_du_encoder.h` declares the RZ/G2L DU encoder private type and constructor.

## Important APIs, Types, and Functions

`struct rzg2l_du_encoder` embeds `drm_encoder` and stores the `enum rzg2l_du_output`. `to_rzg2l_encoder()` provides container conversion. `rzg2l_du_encoder_init()` creates encoders for DT output nodes.

## Control Flow

KMS init creates encoders through this header and later casts DRM encoder objects back to private encoders when assigning possible CRTCs and clones.

## State and Persistence Behavior

The output enum persists with the DRM encoder and is used for routing decisions and validation.

## Dependencies and Integration Points

It depends on DRM encoder types, Linux `container_of`, and `struct rzg2l_du_device`.

## Risks and Edge Cases

The header references `enum rzg2l_du_output`, so include ordering must provide the enum via the driver header.

## Test Signals

Compile coverage and encoder-list iteration in KMS init are sufficient signals.
