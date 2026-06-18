# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.h

Purpose: small public header for the Venus encoder implementation. It declares the encoder control initialization entry point used by `venc.c`.

Important APIs/types/functions: forward-declares `struct venus_inst` and exports `int venc_ctrl_init(struct venus_inst *inst);`. The include guard is `__VENUS_VENC_H__`.

Control flow: no runtime control flow; it is a compile-time interface between the encoder core and control registration implementation.

State and persistence: no state is defined here. `venus_inst` ownership and control-handler storage live in shared Venus structures included by `.c` files.

Dependencies and integration: included by `venc.c` and `venc_ctrls.c`. It avoids including full Venus instance definitions, keeping the dependency surface minimal.

Risks: any signature change must be coordinated across the encoder open path and control implementation. Because the header is minimal, hidden coupling exists through `struct venus_inst` fields accessed only in `.c` files.

Test signals: build coverage is the main signal; encoder open should fail cleanly if `venc_ctrl_init()` returns an error from control handler initialization.
