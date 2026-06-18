# File Research: sources/block-storage/util-linux/libmount/src/hooks.c

This file implements libmount's hook dispatcher and registers built-in hooksets. Hooksets provide staged callbacks for source preparation, target preparation, option preparation, mount execution, post-mount work, and final post-processing.

Built-in hook order on Linux:

- `__loopdev`
- `__veritydev` when cryptsetup is enabled
- `__mkdir`
- `__selinux` when libselinux is enabled
- `__subdir`
- `__mount` when mount fd support is enabled
- `__legacy-mount`
- `__idmap` when mount fd and Linux mount headers are available
- `__owner`

Key APIs:

- `mnt_context_deinit_hooksets()` calls every hookset deinitializer and resets hook lists.
- `mnt_context_get_hookset()` finds a built-in hookset by name.
- `mnt_context_set_hookset_data()` and `mnt_context_get_hookset_data()` manage per-hookset global data.
- `mnt_context_append_hook()` appends a staged callback.
- `mnt_context_insert_hook()` appends a staged callback that should run after another hookset name.
- `mnt_context_remove_hook()` removes a matching hook and optionally returns its data.
- `mnt_context_has_hook()` checks for existing active hooks.
- `mnt_context_call_hooks()` invokes first callbacks for a stage, then active callbacks for that stage.

Important behavior:

- Hookset data and individual hook callback data are separate lists.
- Each hook records hookset, stage, data pointer, optional `after` dependency name, callback, and an `executed` bit.
- A hook callback can register more hooks dynamically for any stage.
- `call_depend_hooks()` runs hooks whose `after` field matches the just-called hookset name and stage.
- Positive return codes from first hooks are recoverable and do not abort the stage; negative return codes abort.
- Fake contexts skip callback execution but log fake calls.
- After a stage, executed bits for that stage are reset so hooks can be called again in later cycles if needed.

Dependencies and interactions:

- All hook modules depend on this dispatcher for lifecycle and ordering.
- SELinux uses dependency insertion after `__mkdir`; legacy mount checks whether `__mount` registered active hooks.

Risk notes:

- Dependency matching is by hookset name string, so renaming hooksets can silently break ordered hooks.
- `mnt_context_deinit_hooksets()` sums deinit return values rather than preserving first failure.
