# sources/distributed-fs/ceph-client/arch/m68k/hp300/reboot.S

Purpose: provides the HP300 `hp300_reset` symbol used as the machine reset callback.

Important APIs/types/functions: exported assembly symbol is `hp300_reset`.

Control flow: currently an infinite self-jump (`jmp hp300_reset`). Comments state a real reboot would need to undo early MMU/cache setup and jump back to PROM, but this implementation is explicitly marked non-working.

State and persistence: no state is updated; reset requests spin forever.

Dependencies/integration: `config.c` assigns `mach_reset = hp300_reset`, so architecture reset paths enter this stub.

Risks: any attempt to reboot an HP300 kernel using this callback will hang instead of resetting hardware. Watchdog or external reset is required if available.

Test signals: link symbol resolution, reset path reaches `hp300_reset`, and platform documentation/known-failure tests should treat reboot as unsupported or hanging.
