# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.c

This file is the platform dispatch layer for HFI version-specific capability, codec, frequency, and buffer-requirement callbacks. It maps an `enum hfi_version` to the v4 or v6 platform tables and provides small wrappers used by parser and PM code.

Key functions are `hfi_platform_get()`, `hfi_platform_get_codec_vpp_freq()`, `hfi_platform_get_codec_vsp_freq()`, `hfi_platform_get_codec_lp_freq()`, and `hfi_platform_get_codecs()`. The dispatch target is `struct hfi_platform` from `hfi_platform.h`, with concrete instances in `hfi_platform_v4.c` and `hfi_platform_v6.c`.

Control flow is simple: version lookup returns `hfi_plat_v4`, `hfi_plat_v6`, or `NULL`; wrapper functions guard missing platforms/callbacks and return zero or `-EINVAL` on unsupported versions. `hfi_platform_get_codecs()` additionally masks VP8 on IRIS2_1 cores.

The file stores no state. It reads `core->res->hfi_version` and hardware predicates from `core.h`. Integration points include `hfi_parser.c` static capability loading and `pm_helpers.c` frequency estimation through helper wrappers.

Risks include callback mismatch and silent zero frequencies. `hfi_platform_get_codec_vsp_freq()` checks `codec_vpp_freq` before calling `codec_vsp_freq`, so a platform with only VSP callback would be skipped. Unsupported HFI versions fall back to firmware parser paths where available, but PM frequency lookup may degrade to zero. Test signals include codec enumeration on v4/v6, IRIS2_1 VP8 filtering, and nonzero VPP/VSP/low-power frequencies for supported pixel formats.
