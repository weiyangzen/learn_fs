# sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-rst.h

Purpose: This Renesas R-Car header exposes reset-controller helpers for reading mode pins and setting remote-processor boot addresses.

Important APIs/types/functions: With `CONFIG_RST_RCAR`, it declares `rcar_rst_read_mode_pins(u32 *mode)` and `rcar_rst_set_rproc_boot_addr(u64 boot_addr)`. Disabled stubs return `-ENODEV`.

Control flow: Platform or remoteproc code reads boot mode pins for configuration decisions and writes a remote processor boot address before releasing reset.

State and persistence: Mode-pin state reflects latched hardware boot configuration. Remoteproc boot address is reset-controller state used during processor start.

Dependencies and integration: Integrates with Renesas R-Car reset driver, boot configuration, and remoteproc support.

Risks and test signals: Boot-address mistakes can start firmware at the wrong location. Test mode read errors, disabled build stubs, remoteproc boot, and reset sequencing.
