# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs.h

This header defines the input contract for platform-calculated HFI buffer requirements. It is primarily used by v6 platform support, where the driver computes buffer sizes instead of relying entirely on firmware.

The central type is `struct hfi_plat_buffers_params`. It carries coded and output dimensions, codec, HFI color formats for OPB/DPB, HFI version, VPP pipe count, and a decoder/encoder union. Decoder parameters include max macroblocks, buffer-size limit, secondary-output mode, and interlace state. Encoder parameters include work mode, rate-control type, B-frame count, and ten-bit mode. The exported function is `hfi_plat_bufreq_v6()`.

Control flow is external: helpers populate this struct from a `venus_inst`, then call the platform `bufreq` callback. `hfi_plat_bufreq_v6()` fills a mutable `hfi_buffer_requirements` for input, output, output2, scratch, scratch1, scratch2, and persistent buffers based on session type and buffer type.

There is no persistent state in this header; it defines a transient calculation request. Dependencies are `linux/types.h`, `hfi_helper.h`, and the HFI version/buffer requirement ABI.

Risks involve incomplete or inconsistent parameter population. Wrong DPB/OPB format, pipe count, bit depth, or max-macroblock limits can under-allocate firmware buffers. Test signals include successful v6 decoder and encoder stream-on at multiple resolutions, 10-bit UBWC operation, interlaced decode, multi-pipe routing, and correct minimum buffer counts reported to V4L2.
