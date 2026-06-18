# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.h

Purpose: provides the compressed boot declaration or stub for TDX early detection.

Important APIs and state: declares `early_tdx_detect()` when `CONFIG_INTEL_TDX_GUEST` is enabled; otherwise provides an empty inline.

Control flow: no runtime logic beyond config-gated dispatch.

Dependencies and integration: lets generic compressed boot code call `early_tdx_detect()` unconditionally without adding config ifdefs around every call site.

Risks and test signals: build coverage with `CONFIG_INTEL_TDX_GUEST=y/n` is the main signal. Runtime signal is that non-TDX builds produce no TDX references and TDX builds can override `pio_ops`.
