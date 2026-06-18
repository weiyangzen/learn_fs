# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-mod.c

Purpose: simple support module for livepatch callback demos.

Important APIs/functions: basic `module_init`/`module_exit` with `pr_info` logging.

Control flow: init and exit only log function names. It exists as a named module object for `livepatch-callbacks-demo.c`.

State and persistence: module loaded/unloaded state only.

Dependencies and integration: target module name is referenced by the livepatch callback demo.

Risks: none beyond load-order interactions intentionally shown by the demo.

Test signals: load before or after the livepatch demo and observe callback logs.
