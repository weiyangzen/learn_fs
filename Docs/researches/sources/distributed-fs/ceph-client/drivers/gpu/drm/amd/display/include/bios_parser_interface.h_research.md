# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_interface.h

Purpose: declares the public construction/destruction interface for the AMD display BIOS parser.

Important APIs and control flow: `struct bp_init_data` supplies `dc_context` and raw BIOS pointer. `dal_bios_parser_create()` returns a `struct dc_bios *` for a requested `enum dce_version`, and `dal_bios_parser_destroy()` tears it down through a pointer-to-pointer.

State and persistence behavior: no state in the header; created parser objects encapsulate BIOS parsing state elsewhere. The raw BIOS pointer must remain valid for the parser implementation's expected lifetime.

Dependencies and integration points: includes `dc_bios_types.h` and forward-declares `bios_parser`. Display core uses this interface to acquire VBIOS services for transmitter, clock, connector, and spread-spectrum tables.

Risks and test signals: risks include invalid BIOS pointers, wrong DCE/DCN version selection, lifecycle misuse of pointer-to-pointer destroy, and parser implementation drift from declared API. Test signals include successful parser creation for supported ASIC versions, graceful failure on bad BIOS tables, and no use-after-destroy under display teardown.
