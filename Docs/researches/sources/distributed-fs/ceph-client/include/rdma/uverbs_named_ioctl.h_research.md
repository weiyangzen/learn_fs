# sources/distributed-fs/ceph-client/include/rdma/uverbs_named_ioctl.h

Purpose: Provides naming macros that turn uverbs object/method declarations into module-scoped static symbols using `UVERBS_MODULE_NAME`.

Important APIs/types/functions: `UVERBS_METHOD()`, `UVERBS_HANDLER()`, and `UVERBS_OBJECT()` paste module names into generated symbols. `DECLARE_UVERBS_NAMED_METHOD`, `DECLARE_UVERBS_NAMED_METHOD_DESTROY`, `DECLARE_UVERBS_NAMED_OBJECT`, `DECLARE_UVERBS_GLOBAL_METHODS`, `ADD_UVERBS_METHODS`, and `ADD_UVERBS_ATTRIBUTES_SIMPLE` create uverbs definition tables.

Control flow and state: This header has no runtime state. It builds arrays of attribute pointers and method pointers, then wraps them into `uverbs_method_def` and `uverbs_object_def`. Destroy methods can use the shared `uverbs_destroy_def_handler`.

Dependencies and integration: Depends on `rdma/uverbs_ioctl.h` and must be included only after defining `UVERBS_MODULE_NAME`. Drivers use it to add named driver-specific object trees or attributes to the common uverbs API.

Risks and test signals: Risks include symbol collisions, forgetting `UVERBS_MODULE_NAME`, handler naming mismatches, and accidentally declaring methods without handlers. Build coverage is the main test signal; runtime ioctl smoke tests should verify that added methods and attributes are visible and parse correctly.
