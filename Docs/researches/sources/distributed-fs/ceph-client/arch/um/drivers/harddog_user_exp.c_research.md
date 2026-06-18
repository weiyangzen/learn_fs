<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c

Purpose: conditionally exports the host-watchdog helper symbols when the UML watchdog is built as a module.

Important APIs/types/functions: uses `EXPORT_SYMBOL()` for `start_watchdog`, `stop_watchdog`, and `ping_watchdog` under `IS_MODULE(CONFIG_UML_WATCHDOG)`.

Control flow: there is no runtime control flow beyond module symbol export generation.

State and persistence: no state is owned.

Dependencies and integration points: depends on Linux export macros and `harddog.h`. It lets modular `harddog_kern.o` resolve helper functions that may be built into the UML image.

Risks: missing exports break modular watchdog builds; unconditional exports could expose unnecessary symbols in built-in configurations.

Test signals: build `CONFIG_UML_WATCHDOG=m` and `=y`, inspect module symbol resolution, and load/unload the watchdog module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c -->
