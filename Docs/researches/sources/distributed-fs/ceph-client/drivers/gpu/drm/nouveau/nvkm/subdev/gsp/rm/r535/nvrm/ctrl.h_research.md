# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ctrl.h

Purpose: defines the generic R535 GSP RM control RPC header.

Important type: `rpc_gsp_rm_control_v03_00` carries `hClient`, `hObject`, control command ID, status, parameter size, flags, and a flexible `params[]` payload. Control helpers place command-specific structures behind this header.

Control flow and state: declarative only. The runtime control flow is in `nvkm_gsp_rm_ctrl_get()`, `_push()`, `_wr()`, `_rd()`, and `_done()` users; this header defines the common envelope those helpers transmit.

Dependencies and integration: every R535/R570 control call in this group ultimately relies on this shape: interrupt-table reads, VAS page-directory controls, display queries, FBSR setup, FIFO queries, and GR context/ZCULL controls.

Risks and tests: status, parameter sizing, and flexible-array alignment are global ABI risks. Bad layout can manifest as nearly any RM control failure. Tests should include representative read, write-only, and push/readback controls.
