<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h

## Purpose
`smsir.h` declares the Siano IR state and public hooks used by the core module. It also supplies stubs when rc-core support for Siano is disabled.

## Important APIs, Types, and Functions
`struct ir_t` stores the rc device pointer, name, physical path, optional rc keymap string, timeout, and controller id. The declared APIs are `sms_ir_init()`, `sms_ir_exit()`, and `sms_ir_event()`.

## Control Flow
`smscoreapi.c` embeds `struct ir_t` inside `smscore_device_t` and calls these hooks at device startup, message reception, and unregister. With `CONFIG_SMS_SIANO_RC` disabled, inline stubs make those calls compile away behaviorally.

## State and Persistence Behavior
The header defines per-device transient IR state. It does not own persistence or global lists.

## Dependencies and Integration Points
The header depends on Linux input and media rc-core types and forward-declares `smscore_device_t`. It is included by `smscoreapi.h`, so changes here affect the central Siano core type.

## Risks and Test Signals
The stubs must remain behaviorally safe for builds without RC support. The `phys` buffer is 32 bytes and receives `devpath` plus `/ir0`, so long devpaths can be truncated by safe string helpers. Test signals include builds with `CONFIG_SMS_SIANO_RC=y/m/n` and correct board keymap propagation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h -->
