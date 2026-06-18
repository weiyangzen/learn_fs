# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.h

Purpose: declares the ImgTec raw-decoder private state and entry points, with build-time stubs for configurations without raw ImgTec IR support.

Important APIs, types, and functions: `struct img_ir_priv_raw` contains the raw `rc_dev`, echo `timer_list`, and last sampled status. `img_ir_raw_enabled()` returns whether a raw rc-core device is active. The declared implementation hooks are `img_ir_isr_raw()`, `img_ir_setup_raw()`, `img_ir_probe_raw()`, and `img_ir_remove_raw()`. The disabled stubs return false or no-op, with probe returning `-ENODEV`.

Control flow: `img-ir.h` embeds `struct img_ir_priv_raw` inside the platform private data. The core driver can call the raw hooks unconditionally; this header makes those calls compile out when `CONFIG_IR_IMG_RAW` is off.

State and persistence behavior: when enabled, state is runtime-only and bound to the platform device. When disabled, the struct is empty and no state exists.

Dependencies and integration points: forward-declares `struct img_ir_priv` to avoid including the full core header. It integrates with `img-ir-raw.c` and the unlisted platform core ISR/setup paths.

Risks and edge cases: callers should use `img_ir_raw_enabled()` or tolerate stubs. Probe returning `-ENODEV` is expected in disabled builds and should not be reported as a hardware failure unless raw support was required.

Test signals: compile both enabled and disabled configurations and verify the core driver builds without conditional call sites.
