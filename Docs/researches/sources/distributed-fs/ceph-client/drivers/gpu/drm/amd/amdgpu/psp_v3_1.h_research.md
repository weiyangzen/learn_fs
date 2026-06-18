# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.h

Purpose: declares PSP v3.1 setup and several legacy PSP firmware-directory alignment constants.

Important APIs/types/functions: defines enum constants `PSP_DIRECTORY_TABLE_ENTRIES = 4`, `PSP_BINARY_ALIGNMENT = 64`, `PSP_BOOTLOADER_1_MEG_ALIGNMENT = 0x100000`, and `PSP_BOOTLOADER_8_MEM_ALIGNMENT = 0x800000`; declares `void psp_v3_1_set_psp_funcs(struct psp_context *psp);`.

Control flow: no executable flow. Constants are used by PSP firmware layout/parsing expectations in the wider PSP stack, while the setter installs v3.1 callbacks.

State and persistence behavior: no state. Runtime effect is through assigning `psp->funcs` in the implementation.

Dependencies and integration points: includes `amdgpu_psp.h` and integrates with older Vega PSP discovery/setup.

Risks and test signals: alignment constants are hardware/firmware ABI assumptions; changing them can break firmware loading. Test signals are firmware descriptor parsing, build coverage, and correct function-table selection on v3.1 devices.
