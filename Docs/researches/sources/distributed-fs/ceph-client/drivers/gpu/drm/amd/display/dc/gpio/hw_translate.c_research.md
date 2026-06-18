# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.c

Purpose: Dispatches GPIO offset/id translation initialization to the ASIC-generation-specific implementation for the active DCE/DCN version.

Important APIs and functions: `dal_hw_translate_init` accepts a `hw_translate`, `dce_version`, and environment, then assigns the proper function table by calling generation-specific initializers such as `dal_hw_translate_dce80_init`, `dal_hw_translate_dcn32_init`, or `dal_hw_translate_dcn42_init`.

Control flow: a single switch maps version enums to initialization functions. Several version groups share one translation implementation. Unsupported versions hit `BREAK_TO_DEBUGGER()` and return false. `CONFIG_DRM_AMD_DC_SI` conditionally includes and enables DCE6 support.

State and persistence: state is only the `translate->funcs` pointer initialized by the selected backend. The environment parameter is currently unused. No persistent state or register writes occur in this dispatcher.

Dependencies and integration: includes GPIO types, `hw_translate.h`, and all supported generation-specific translator headers. It sits between generic GPIO discovery and ASIC register-offset mapping used by GPIO factories/managers.

Risks and test signals: adding a new DCN version without updating this switch leaves GPIO translation unavailable. Tests should instantiate each supported `dce_version`, verify `funcs` is non-null, and cover build configurations with and without `CONFIG_DRM_AMD_DC_SI`.
