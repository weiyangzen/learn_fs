# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_binarydesc.c

Purpose: implements binary descriptor construction for CSS pipeline stages and computes Bayer downscaling factors.

Important APIs/types/functions: the internal `pipe_binarydesc_get_offline()` initializes common descriptor defaults. Public builders specialize descriptor mode, online/continuous/two-ppc flags, stream format, frame formats, BDS info, DVS/DZ/TNR/DPC/YUV downscale flags, high-speed/reduced-pipe flags, and ISP pipe version. `bds_factors_list`, `sh_css_bds_factor_get_fract()`, and `binarydesc_calculate_bds_factor()` map enum factors to rational scales and select a factor by resolution.

Control flow: each builder copies or derives `in_info`, `out_info`, `vf_info`, and optional `bds_out_info`, then calls the common initializer and applies mode-specific fields. Preview/video paths compute effective input size and raw bit depth, choose copy mode for YUV input, optionally compute or default raw binning BDS, update `pipe->required_bds_factor`, and disable BDS info when fractional downscale is enabled. Primary/capture/GDC/ANR helpers adapt frame format and raw bit depth for their stage.

State and persistence: mostly stack/output-parameter mutation. Persistent side effects are `pipe->required_bds_factor` and any caller-observed frame-info changes.

Dependencies and integration: depends on CSS frame format/public APIs, pipe config, input-format utilities, debug tracing, `sh_css_params`, and GDC constants. It feeds firmware binary selection and later stage descriptor assembly.

Risks and test signals: many assertions document non-null expectations, but some comments allow nulls. `binarydesc_calculate_bds_factor()` uses integer division and a fixed rounding margin, so edge resolutions can fail or choose unexpected factors. Tests should cover preview/video raw binning, fractional downscale, YUV copy fallback, online two-ppc streams, primary HQ stage bounds, and each frame-format conversion.
