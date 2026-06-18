# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/src/util.c

Purpose: implements CSS utility validation and atomisp input-format classification.

Important APIs/types/functions: `ia_css_util_input_format_bpp()` maps atomisp input formats to bit depth, `ia_css_util_check_vf_info()` and `ia_css_util_check_vf_out_info()` validate frame info, `ia_css_util_check_res()` rejects zero or odd widths, `ia_css_util_res_leq()` compares dimensions, `ia_css_util_resolution_is_zero()` tests either dimension zero, `ia_css_util_is_input_format_raw()`/`_yuv()` classify formats, and `ia_css_util_check_input()` validates stream configuration against raw/YUV requirements.

Control flow: most helpers are switch or predicate logic. Frame checks delegate to `ia_css_frame_check_info()` and `ia_css_binary_max_vf_width()`. Input validation rejects missing stream configs, zero effective resolution, and mismatched required formats.

State and persistence: no state; all behavior is derived from arguments.

Dependencies and integration: used by pipe descriptor code and stream validation before firmware binary selection.

Risks and test signals: `ATOMISP_INPUT_FORMAT_RGB_565` maps to `65`, likely a typo for 16 and a high-risk value if used. Raw 14/16 are deliberately not raw ISP inputs except copy paths. Tests should cover every enum mapping, two-ppc RAW14/RAW16 behavior, odd width rejection with odd height allowance, and raw/YUV classification drift.
