# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.c

## Purpose
`lpass-macro-common.c` provides shared helpers for Qualcomm LPASS macro codec drivers. It centralizes attachment and activation of optional power domains and stores a process-wide LPASS codec-version value used by macro drivers such as RX/TX/WSA/VA to select register layouts and feature behavior.

## Important APIs, Types, And Functions
The exported APIs are `lpass_macro_pds_init()`, `lpass_macro_pds_exit()`, `lpass_macro_set_codec_version()`, and `lpass_macro_get_codec_version()`. `lpass_macro_pds_init()` returns a `struct lpass_macro` containing attached `"macro"` and `"dcodec"` power-domain devices, or `NULL` if the device has no `power-domains` property. Version state is a static `enum lpass_codec_version` protected by `lpass_codec_mutex`.

## Control Flow
Power-domain initialization first checks device tree for `power-domains`; absence means the caller should continue without domain handles. If present, it allocates `struct lpass_macro`, attaches the `"macro"` domain, runtime-resumes it, attaches the `"dcodec"` domain, and runtime-resumes it. Each failure path unwinds only the resources already acquired. Exit performs the reverse `pm_runtime_put()` and `dev_pm_domain_detach()` operations when the handle is non-NULL. Codec-version setters/getters lock around the static global value.

## State And Persistence
The helper persists two kinds of state: per-device power-domain handles in `struct lpass_macro`, owned by the caller, and one global codec-version enum shared by all users in the kernel image. Power-domain runtime state persists until `lpass_macro_pds_exit()`. The codec version defaults to zero (`LPASS_CODEC_VERSION_UNKNOWN`) until some other code calls `lpass_macro_set_codec_version()`.

## Dependencies And Integration Points
The file depends on Linux device tree helpers, generic PM domains, runtime PM, platform device headers, and the declarations in `lpass-macro-common.h`. It exports symbols with GPL visibility for other LPASS macro modules. `lpass-rx-macro.c` uses `lpass_macro_pds_init()` during probe, registers `lpass_macro_pds_exit_action()` as a managed cleanup action, and reads `lpass_macro_get_codec_version()` to choose register defaults and strides.

## Risks And Notes
`lpass_macro_pds_exit()` assumes both `macro_pd` and `dcodec_pd` are valid when `pds` is non-NULL; callers should only pass objects returned successfully by init. The codec version is global rather than per-device, which is simple for single-codec systems but risky if multiple LPASS codec generations coexist. If no provider sets the version before a macro probes, consumers may reject probe as unsupported.

## Test Signals
Tests should cover devices with and without `power-domains`, failure injection for each attach/resume step, balanced runtime-PM puts on removal, and version set/get behavior under concurrent callers. Integration tests should verify macro drivers probe successfully only after the expected codec version has been established.
