## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/hsmp.h`

Purpose: exposes the AMD HSMP message-sending kernel API, with a stub when the driver is disabled.

Important APIs and types: includes UAPI `asm/amd_hsmp.h` for `struct hsmp_message`; declares `hsmp_send_message()` when `CONFIG_AMD_HSMP` is enabled, otherwise provides an inline `-ENODEV` stub.

Control flow: no runtime logic in enabled builds; disabled builds immediately fail calls.

State and persistence: HSMP state is owned by the implementation driver, not this header.

Dependencies and integration points: AMD HSMP platform driver and any kernel subsystem sending HSMP mailbox messages.

Risks: callers must handle `-ENODEV` because the helper may compile out. UAPI structure layout must remain compatible with HSMP firmware expectations.

Test signals: builds with and without `CONFIG_AMD_HSMP`, HSMP message success on supported AMD servers, and caller fallback on `-ENODEV`.
