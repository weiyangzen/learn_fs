# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.h

Purpose: this header defines PSP/RAS TA state, memory descriptors, function tables, firmware load/unload request structures, and public PSP APIs.

Important types: `struct ras_ta_image_header` exposes TA image version at offset 0x60. `struct ras_psp_sys_status` carries preloaded TA state and an external PSP mutex. `struct ras_ta_init_param` mirrors startup flags. `struct gpu_mem_block` describes shared GPU memory allocations with refcount. `struct ras_psp_ctx`, `ras_ta_ctx`, and `ras_psp` hold command/fence/firmware memory, locks, sessions, firmware metadata, selected IP/sys functions, and TA initialization state. `struct ras_psp_ta_load` and `ras_psp_ta_unload` are caller request/response containers.

Control flow and state: no active code lives here, but the structures define memory ownership and session state used by `ras_psp.c`. Persistence is not stored here; state is volatile and reset-sensitive.

Dependencies and integration: includes `ras_ta_if.h` and `ras.h`; used by core, UMC address translation, GFX error injection, and firmware loaders. Risks include ambiguous ownership of `bin_addr`, unchecked `void *` mutex/device fields, and tight coupling to PSP GFX ring command structures provided elsewhere. Test signals should compile all transport paths and include structure-size/field-offset checks where firmware ABI requires fixed layout.
