# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor_regs.h

Purpose: register definition header for i915 cursor hardware. It centralizes MMIO offsets and bit fields for legacy CURCNTR/CURBASE/CURPOS/CURSIZE, modern MCURSOR controls, CUR_FBC_CTL, cursor watermarks/DDB, and PSR selective fetch cursor control.

Important definitions: `CURCNTR()`, `CURBASE()`, `CURPOS()`, `CURPOS_ERLY_TPT()`, `CURSIZE()`, `CUR_FBC_CTL()`, `CURSURFLIVE()`, `CUR_WM()`, `CUR_WM_TRANS()`, `CUR_WM_SAGV()`, `CUR_WM_SAGV_TRANS()`, `CUR_BUF_CFG()`, and `SEL_FETCH_CUR_CTL()`. Bit helpers encode enable, pipe gamma/CSC, pipe select, rotate-180, trickle-feed disable, cursor modes, signed position fields, FBC height, watermark enable/lines/blocks, and cursor DDB start/end.

Control flow and state: this header has no runtime control flow and stores no state. It provides typed MMIO macros consumed by `intel_cursor.c` and related display register code.

Dependencies and integration: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_MMIO_CURSOR2`, `REG_BIT`, `REG_GENMASK`, and field-prep helpers. The definitions map directly to hardware programming in cursor update and error-capture paths.

Risks: register encodings vary by display generation; comments document several generation boundaries such as old desktop 8xx control fields, new MCURSOR fields, IVB+ FBC control, SKL+ watermark registers, and TGL+ selective fetch. Incorrect field masks would corrupt hardware programming, so generation-specific callers must keep using the right fields.

Test signals: compile-time use by cursor programming plus runtime cursor movement/shape/watermark tests across pre-i9xx, i9xx/g4x, IVB+, SKL+, TGL+, and MTL+ hardware. Error-state capture should show sane CUR* register values.
