# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-filter.h

Purpose: defines BDISP filter coefficient structure shapes and standard RGB/YUV conversion matrix constants.

Important APIs and types: `BDISP_HF_NB` and `BDISP_VF_NB` define horizontal and vertical coefficient counts. `struct bdisp_filter_h_spec` and `struct bdisp_filter_v_spec` store fixed-point scale factor min/max values and coefficient arrays. Static arrays `bdisp_rgb_to_yuv` and `bdisp_yuv_to_rgb` hold four 32-bit matrix words for BT.601-style conversion.

Control flow: hardware programming and debug code include this header to describe filter tables and to recognize or program standard color-conversion matrices. `bdisp-debug.c` compares IVXM register values against these arrays to print RGB-to-YUV or YUV-to-RGB labels.

State and persistence: the header defines static const data per translation unit that includes it. There is no mutable state.

Dependencies and integration points: depends on kernel integer typedefs such as `u8`, `u16`, and `u32` supplied by including files. Integrates BDISP scaling/filter code and debug interpretation with the same coefficient and matrix definitions.

Risks: the header has no include guard, so multiple inclusion in one translation unit would redefine structs and static arrays. Static const arrays in a header create a private copy per including C file. Matrix values must match hardware register encoding and colorimetry expectations.

Test signals: compile coverage for all includers; scaling tests that select expected coefficient specs; debugfs IVXM decoding for known conversion matrices; and visual/color validation for RGB/YUV blits.
