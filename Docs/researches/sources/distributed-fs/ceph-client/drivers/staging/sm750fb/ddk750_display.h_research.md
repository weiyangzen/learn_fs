# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.h

Purpose: defines bit-encoded SM750 logical display output selections and declares the display-routing API.

Important APIs/types/functions: macros define offsets, masks, usage bits, and encoded values for panel-to-primary/secondary, CRT-to-primary/secondary, primary/secondary timing-plane enable, panel sequence, dual TFT, DAC, and DPMS. `enum disp_output` provides common output recipes such as `do_LCD1_PRI`, `do_LCD1_SEC`, `do_LCD2_PRI`, `do_LCD2_SEC`, `do_CRT_PRI`, and `do_CRT_SEC`. Public API is `ddk750_set_logical_disp_out()`.

Control flow: no runtime flow in the header; `ddk750_display.c` interprets usage bits to decide which hardware fields to update.

State and persistence: encoded constants represent desired hardware register changes but store no state.

Dependencies and integration: relies on `BIT()` and register semantics from the SM750 headers. Used by framebuffer output configuration to select active heads.

Risks: the low 16 bits carry values while shifted masks in high bits indicate usage; callers can OR incompatible recipes and request inconsistent routing. Some output comments mention DVI/DSUB behavior tied to DAC control, so board wiring assumptions matter.

Test signals: compile each enum recipe, verify expected register writes for every recipe, and test invalid or combined recipes defensively at call sites.
