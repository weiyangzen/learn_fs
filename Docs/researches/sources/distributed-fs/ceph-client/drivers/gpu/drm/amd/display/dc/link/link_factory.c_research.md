# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.c

## Purpose

`link_factory.c` constructs and destroys `struct link_service` and `struct dc_link` objects. It centralizes link service function-pointer wiring, BIOS/object-table based physical link construction, USB4 DPIA link construction, resource tracking, DDC/panel/link-encoder allocation, connector signal classification, and destruction cleanup.

## Important APIs, Types, And Functions

- `link_create_link_service()` allocates a `struct link_service` and fills all function pointers through category-specific constructors.
- `link_destroy_link_service()` frees the service.
- Constructor groups assign factory, detection, resource, validation, DPMS, DDC, DP capability, DP PHY/DPIA, IRQ, eDP panel control, panel replay, DP CTS, and DP trace functions.
- `link_create()` allocates a `dc_link` and calls `link_construct()`.
- `construct_phy()` builds physical connector links from BIOS connector/source objects, DDC, HPD, link encoder, panel control, device tags, external display path metadata, and HPD filters.
- `construct_dpia()` builds synthetic USB4 DPIA links with flexible DIG mapping and DPIA DDC service.
- `link_destroy()` calls `link_destruct()`, frees sinks/resources, and nulls the pointer.

## Control Flow

Service construction is simple allocation plus a fixed sequence of function-pointer category initializers. Physical link construction validates supported encoder or analog engine, reads connector caps, creates DDC, resolves HPD IRQs, creates a link encoder, maps connector IDs to signal types, creates panel control for eDP/LVDS, finds supported device tags, reads external display path channel mapping/chip caps, records forced fixed-VS drive settings, programs HPD filter, and initializes PSR/replay defaults. Failure jumps release partially created resources.

DPIA construction uses a dummy DisplayPort connector object, marks the endpoint as `DISPLAY_ENDPOINT_USB4_DPIA`, enables flexible DIG mapping, creates a DPIA DDC service without physical DDC, records the DPIA port index, and sets unsupported PSR/replay defaults.

## State And Persistence Behavior

The file initializes persistent in-memory link fields used throughout DC: IDs, endpoint type, connector signal, DDC service, HPD IRQ sources, link encoder, panel control, encoder/resource tracking arrays, channel mapping, chip caps, BIOS-forced drive settings, device tags, PSR/replay defaults, and DPIA preferred engine. Destruction releases DDC, panel control, link encoder, local/remote sinks, and resource-pool tracking entries. No on-disk state is written.

## Dependencies And Integration Points

It includes all link submodule headers, GPIO/BIOS/Atom firmware support, and resource-pool factory hooks. It is the integration point that turns standalone link submodule functions into the `dc->link_srv` service table used across detection, validation, DPMS, training, DDC, panel control, and diagnostics.

## Risks And Edge Cases

- Link construction has many partially initialized failure paths; cleanup must match allocation order.
- Physical construction assumes BIOS object tables provide coherent connector, encoder, HPD, and device-tag data.
- SmartMux restricts dual eDP creation in this path.
- External DP bridge handling rewrites connector signal to DP and follows nested source objects.
- Resource pool link encoder tracking is updated only for non-flexible physical encoders and must stay balanced on destruction.
- DPIA links intentionally omit physical link encoders and HPD IRQs, so downstream code must honor endpoint type.

## Test Signals

Build tests catch service signature drift. Runtime tests should cover service creation/destruction, physical HDMI/DP/eDP/LVDS/VGA/DVI links, external DP bridge links, unsupported encoder failure, panel control creation failure, HPD IRQ mapping, fixed-VS chip caps and BIOS drive settings, DPIA construction, and link destruction reference/resource cleanup.
