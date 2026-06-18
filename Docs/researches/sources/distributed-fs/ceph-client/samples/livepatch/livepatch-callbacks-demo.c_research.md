# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-demo.c

Purpose: livepatch sample demonstrating pre/post patch and unpatch callbacks for vmlinux and module objects.

Important APIs/functions: `struct klp_patch`, `struct klp_object`, `struct klp_func`, callbacks `.pre_patch`, `.post_patch`, `.pre_unpatch`, `.post_unpatch`, `klp_enable_patch`, `MODULE_INFO(livepatch, "Y")`, and module parameter `pre_patch_ret`.

Control flow: init enables a patch containing callback-only objects for vmlinux and `livepatch_callbacks_mod`, plus a patch for `livepatch_callbacks_busymod:busymod_work_func`. Callback helpers log object/module state and `pre_patch_ret` can force failure. Exit does nothing; disabling is controlled through livepatch sysfs.

State and persistence: registered livepatch remains managed by livepatch core until disabled/removed.

Dependencies and integration: targets support modules by name and demonstrates livepatch sysfs enable/disable behavior.

Risks: nonzero pre-patch return can reject module loading/patching. Target symbol names must match. Empty module exit is standard for livepatch but surprises ordinary module expectations.

Test signals: follow source usage comments, vary load order and `pre_patch_ret`, and watch callback order/state logs.
