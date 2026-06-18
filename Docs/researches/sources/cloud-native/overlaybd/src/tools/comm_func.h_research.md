# sources/cloud-native/overlaybd/src/tools/comm_func.h

Purpose: declares shared OverlayBD CLI helper APIs and imports the common Photon, LSMT, zfile, image-service, and CLI11 dependencies used by tool front ends.

Important APIs/types/functions: prototypes `open_file`, `create_overlaybd`, `create_uploader`, `create_ext4fs`, `is_erofs_fs`, `create_erofs_fs`, and `parse_config_and_dev_id`; also declares an unused `generate_option(CLI::App&)`.

Control flow: as a header it only exposes helper contracts. Defaults let callers open from local FS when no `IFileSystem` is supplied and use mode `0` unless needed.

State and persistence: no state; it defines pointer-based ownership interfaces returning raw Photon objects that callers must delete.

Dependencies/integration: common include for OverlayBD tools that need image-service access, zfile compression/upload, Photon lifecycle, or CLI11 option wiring.

Risks: broad includes increase compile coupling. Raw pointers and fail-fast implementation semantics are not documented in the header, so callers must learn ownership and error behavior from `comm_func.cpp`.

Test signals: compile coverage catches signature drift; runtime coverage comes from the tools using the helpers.
