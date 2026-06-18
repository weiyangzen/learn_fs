# sources/distributed-fs/ceph-client/include/uapi/linux/media/amlogic/c3-isp-config.h

Purpose: defines the Amlogic C3 ISP userspace ABI for 3A statistics buffers and V4L2 ISP parameter blocks.

Important APIs and types: max-zone constants define AE/AF/AWB grid sizes and coordinate counts. Statistics structs include AWB ratio zones, AE 5-bin zone histograms plus 1024-bin global histogram, AF contrast metrics with mantissa/exponent bitfields, and aggregate `struct c3_isp_stats_info`. Parameter ABI includes version `C3_ISP_PARAMS_BUFFER_V0`, block types for AWB gains/config, AE config, AF config, post gamma, CCM, CSC, and BLC, block-header alias `c3_isp_params_block_header`, per-block enable/disable flags, parameter structs with explicit alignment, `C3_ISP_PARAMS_MAX_SIZE`, and `struct c3_isp_params_cfg`.

Control flow: userspace receives metadata buffers containing AWB/AE/AF stats, computes updated ISP tuning, then submits a `c3_isp_params_cfg` buffer containing one or more typed parameter blocks. Each block header tells the driver how to parse and enable/disable a block.

State and persistence: stats buffers are per-frame capture output. Parameter buffers configure runtime ISP hardware state such as gains, metering grids, gamma LUT, color matrices, and black-level offsets. Settings are not persistent unless userspace reapplies them.

Dependencies and integration points: depends on `linux/types.h`, `linux/media/v4l2-isp.h`, and kernel-only build assertions. Integrates V4L2 metadata formats, ISP params buffers, Amlogic C3 camera pipeline, 3A algorithms, and userspace camera stacks.

Risks and test signals: risks include struct alignment/packing drift, bitfield portability, mismatched `v4l2_isp_params_block_header`, incorrect max-size calculation, nonzero reserved fields, zone coordinate bounds, fixed-point scale mistakes, and block ordering/size parsing bugs. Test compile-time size assertions, metadata buffer size, all block types individually and combined, reserved zero validation, max zone counts, malformed headers, and frame-to-frame parameter application.
