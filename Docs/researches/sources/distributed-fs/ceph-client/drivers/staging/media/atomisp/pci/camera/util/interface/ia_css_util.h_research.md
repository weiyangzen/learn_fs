# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/interface/ia_css_util.h

Purpose: declares common CSS validation and format utility helpers.

Important APIs/types/functions: public functions include `ia_css_convert_errno()`, `ia_css_util_check_vf_info()`, `ia_css_util_check_input()`, `ia_css_util_check_vf_out_info()`, `ia_css_util_check_res()`, `ia_css_util_res_leq()`, `ia_css_util_resolution_is_zero()`, `ia_css_util_input_format_bpp()`, `ia_css_util_is_input_format_raw()`, and `ia_css_util_is_input_format_yuv()`.

Control flow: no implementation in the header. Callers use these checks before stream/pipe construction and descriptor selection.

State and persistence: none.

Dependencies and integration: depends on CSS error, frame, stream, and atomisp input-format types.

Risks and test signals: validation semantics determine which formats/resolutions reach firmware. Tests should cover raw/YUV requirements, zero and odd dimensions, viewfinder maximum width, and unsupported formats.
