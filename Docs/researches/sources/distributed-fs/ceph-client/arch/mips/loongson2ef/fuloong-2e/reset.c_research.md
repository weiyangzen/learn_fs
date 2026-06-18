<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c

Purpose: Provides Fuloong 2E board preparation hooks for reboot and shutdown.

Important APIs/types/functions: `mach_prepare_reboot()` toggles bit 2 in `LOONGSON_GENCFG`; `mach_prepare_shutdown()` is empty.

Control flow: Reboot clears and sets the reset-related GENCFG bit before common code jumps to boot firmware.

State and persistence: Mutates chipset GENCFG only during restart.

Dependencies and integration: Called by common `loongson_restart()` and `loongson_poweroff()`.

Risks: Shutdown has no power-control action, so poweroff relies on generic halt behavior.

Test signals: Reboot should reset board logic and return to firmware; poweroff should not claim to cut power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c -->
