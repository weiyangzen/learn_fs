# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_devlink.h

Purpose: declares the RVU AF devlink support structures and public registration functions used by `rvu_devlink.c` and the wider RVU driver. It centralizes health reporter operation boilerplate and defines the event-context layout for NPA and NIX devlink health reporting.

Important APIs/types/functions: `RVU_REPORTERS(_name)` expands to a static `struct devlink_health_reporter_ops` with `.name`, `.recover`, and `.dump` tied to the conventional `rvu_<name>_recover` and `rvu_<name>_dump` functions. `enum npa_af_rvu_health` and `enum nix_af_rvu_health` define reporter classes for RVU, general, error, and RAS interrupt groups. `struct rvu_npa_event_ctx` and `struct rvu_nix_event_ctx` store the last captured interrupt register values. `struct rvu_npa_health_reporters` and `struct rvu_nix_health_reporters` hold event context pointers, four devlink health reporter pointers, and four work items. `struct rvu_devlink` binds the devlink instance, owning `struct rvu`, devlink workqueue, and NPA/NIX reporter containers. Public prototypes are `rvu_register_dl(struct rvu *rvu)` and `rvu_unregister_dl(struct rvu *rvu)`.

Control flow: this header does not execute logic itself; it defines the structure that `rvu_register_dl()` fills, interrupt handlers update, work items report, and `rvu_unregister_dl()` tears down. The macro enforces a naming convention so each reporter declaration in the C file can be one line once matching dump/recover functions exist.

State and persistence: the structures describe runtime-only state attached to the PCI driver instance. Event contexts persist the most recent NPA/NIX interrupt values until overwritten or freed. Work structs are embedded in reporter containers and queued on the shared devlink workqueue. No persistent storage is represented.

Dependencies and integration: depends on devlink health reporter types, workqueue types, and the forward declaration/definition of `struct rvu` from RVU headers included by users. It is included by RVU devlink implementation code and indirectly shapes AF probe/remove behavior through `rvu_register_dl` and `rvu_unregister_dl`.

Risks: the macro relies on exact function naming and only supports `.recover` and `.dump`; adding reporter callbacks needs macro changes or manual ops. The NPA/NIX reporter container layouts are parallel but independent, so changes must be kept symmetric where intended. `struct rvu_devlink` has a single `devlink_wq` shared by both NPA and NIX paths, so ownership must be clear in implementation to avoid leaks or use-after-free.

Test signals: compile coverage catches macro naming mismatches and missing dump/recover functions. Runtime probe/remove tests should verify all embedded work items are initialized before IRQs can queue them and that event contexts/reporters are allocated and freed consistently for both NPA and NIX.
