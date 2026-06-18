# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ObjectID.h

Purpose: This header defines Radeon/ATOM BIOS graphics object IDs for GPUs, encoders, connectors, routers, and generic objects, plus macros for composing BIOS object enum IDs.

Important APIs, types, and functions: Defines object type values, encoder object IDs, connector object IDs, router/generic IDs, enum IDs, object bit masks/shifts, `CONSTRUCTOBJECTFAMILYID()`, and many `*_ENUM_ID*` constants such as internal LVDS/TMDS/DAC/UNIPHY encoders and DVI/VGA/HDMI/DisplayPort/eDP/MXM connectors.

Control flow: No executable control flow. Driver code includes these macros to decode ATOM BIOS object tables and map BIOS-described display topology to DRM encoder/connector objects.

State and persistence: No runtime state. Numeric constants are ABI-like vocabulary shared with BIOS table contents and must remain stable.

Dependencies and integration points: Used by Radeon ATOM BIOS parsing and display/connector setup code. Values correspond to AMD internal ObjectID definitions and BIOS object table encodings.

Risks: Numeric changes break BIOS parsing for real hardware. Some aliases intentionally share values, such as ALMOND and NUTMEG object IDs, and comments document shared DAC/TV/LVDS/eDP cases. `_X86_` packing pragmas are legacy and should not be casually altered.

Test signals: Parse ATOM BIOS object tables across Radeon generations; compare decoded connector/encoder topology with expected board outputs; compile all architectures that include the header; regression-test HDMI/DP/eDP/LVDS/MXM mappings.
