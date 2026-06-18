# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.h

Purpose: declares the shared BIOS object-ID conversion API and includes the type definitions needed by both parser implementations.

Important API: `struct graphics_object_id object_id_from_bios_object_id(uint32_t bios_object_id);`.

Control flow and integration: the header is included by `bios_parser.c`, `bios_parser2.c`, and the implementation file. It intentionally exposes only the conversion API, keeping all mapping tables private to `bios_parser_common.c`.

State, dependencies, risks, and tests: no state. Depends on `dm_services.h` and `ObjectID.h`. Risks are compile/API drift if graphics object definitions move. Test signals are compile coverage for both parser implementations and direct conversion tests through the exported function.
