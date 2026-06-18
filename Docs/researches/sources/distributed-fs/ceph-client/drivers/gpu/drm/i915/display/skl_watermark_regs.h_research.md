# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark_regs.h

Purpose: defines MMIO registers and bit fields for SKL+ DBUF, MBUS, watermark latency, and package C-state latency control. It is the register companion for `skl_watermark.c`.

Important APIs/types/functions: main register macros include `PIPE_MBUS_DBOX_CTL()`, `MBUS_UBOX_CTL`, `MBUS_BBOX_CTL_S1`, `MBUS_BBOX_CTL_S2`, `MBUS_CTL`, `DBUF_CTL_S()`, `MTL_LATENCY_LP0_LP1`, `MTL_LATENCY_LP2_LP3`, `MTL_LATENCY_LP4_LP5`, `MTL_LATENCY_SAGV`, and `LNL_PKG_C_LATENCY`. Bit fields cover MBUS DBOX transaction throttling, A/B/I/BW credits, MBUS join and hash mode, join pipe selection, translation throttle minimum, DBUF power request/state, tracker-state service fields, MTL latency pairs, SAGV QCLK latency, and Lunar Lake package C latency plus added wake time.

Control flow: watermark code uses these macros to read latency values, inspect or update DBUF power state, program MBUS joining and pipe selection, update tracker service ratios when CDCLK/MDCLK changes, configure DBOX credits for active pipes, and program package C-state latency for display power behavior.

State and persistence behavior: the header has no software state. Values written through these macros persist in hardware registers across display power/runtime sequences until reset, firmware, or driver code changes them. Some fields have generation-specific widths, such as Xe3P versus older DBUF minimum tracker service masks and MBUS translation throttle fields.

Dependencies and integration points: depends on `intel_display_reg_defs.h`. It is consumed by watermark/DBUF code and indirectly by CDCLK, power, and atomic commit paths that coordinate with DBUF and MBUS state.

Risks: incorrectly selecting older versus Xe3P field masks can corrupt unrelated bits. MBUS join state must match DBUF slice allocation and CDCLK state or underruns/hangs are possible. Latency register fields are packed pairs, so parsing even/odd levels incorrectly would invalidate all watermark calculations.

Test signals: register dumps across MBUS join/unjoin, DBUF slice enable/disable, latency readout logs, package C latency writes on display 20+, KMS underrun checks, and hardware-state verification after modesets.
