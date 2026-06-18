# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_local.h

Purpose: defines a state snapshot for the CSS 2401 pixel generator controller.

Important APIs/types/functions: `pixelgen_ctrl_state_t` stores common enable, PRBS seed registers, sync-generator SID/free-run/pause/frame/pixel/line/blanking/status fields, and TPG mode/mask/delta/color registers.

Control flow: no direct flow. Private helpers read these fields from pixelgen registers and dump them.

State and persistence: snapshot-only; actual pixel generator configuration persists in hardware registers.

Dependencies and integration: depends on `pixelgen_global.h` for public config types and HRT data types.

Risks and test signals: state structure must stay aligned with `PixelGen_SysBlock_defs.h`. Tests should capture/dump PRBS, sync generator, and TPG modes.
