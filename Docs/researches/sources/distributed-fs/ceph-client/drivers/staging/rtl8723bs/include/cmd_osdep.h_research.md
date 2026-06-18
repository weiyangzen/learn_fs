# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/cmd_osdep.h

Purpose: this header declares OS-dependent command/event queue initialization, cleanup, enqueue, and dequeue hooks for the Realtek command subsystem.

Important APIs/types/functions: prototypes include `rtw_init_cmd_priv`, `rtw_init_evt_priv`, `_rtw_free_evt_priv`, `_rtw_free_cmd_priv`, `_rtw_enqueue_cmd`, and `_rtw_dequeue_cmd`. The referenced types are `cmd_priv`, `evt_priv`, `__queue`, and `cmd_obj`, all provided by the broader driver includes.

Control flow and integration: this header has no implementation. `drv_types.h` includes it between `rtw_cmd.h` and the adapter definition, making these functions visible to core command-thread and event-thread setup/teardown code. The HAL files in this subset integrate indirectly through C2H work commands and firmware H2C command paths.

State and persistence: command and event state is owned by `struct adapter.cmdpriv` and `struct adapter.evtpriv`; this header only declares lifecycle operations for that state.

Dependencies: depends on prior declarations from `rtw_cmd.h`, queue helpers, and OS service types included by `drv_types.h`.

Risks and test signals: this header is small, but ordering matters because it uses incomplete driver types. Mismatched enqueue/dequeue locking semantics would affect C2H events, scan/join commands, and transmit aggregation requests. Tests should cover command/event init/free symmetry, enqueue/dequeue ordering, and C2H work submission from SDIO interrupt context.
