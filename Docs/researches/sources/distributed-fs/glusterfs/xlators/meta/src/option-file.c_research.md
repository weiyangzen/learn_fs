# sources/distributed-fs/glusterfs/xlators/meta/src/option-file.c

Purpose: implements one virtual file per xlator option, exposing the option value as text.

Important APIs/types/functions: `option_file_fill()` formats `data_to_str(data)` from a `data_t *` stored in inode context. `meta_option_file_hook()` looks up the option by `loc->name` in the parent xlator's `options` dict, stores the `data_t *`, and attaches `option_file_ops`.

Control flow: `options-dir.c` creates dynamic dirents with `meta_option_file_hook`. On lookup, this hook binds the matched dictionary value. On read, the default file path calls `option_file_fill()`.

State and persistence behavior: the file holds a raw pointer to a dictionary value owned by the xlator options dict; it does not copy or persist option data. Fd reads cache the rendered string.

Dependencies and integration points: depends on Gluster dict/data APIs, `meta_ctx_get/set()`, and `data_to_str()`. It integrates with `options-dir.c`.

Risks and edge cases: if an option disappears or has a null value between lookup and read, `data_to_str()` usage can fail. The value is not escaped beyond `data_to_str()`, so binary or unusual option data may render poorly.

Test signals: list `options`, read scalar options, test missing option lookup failure, and verify reopened fds reflect changed option values while already-open fds keep cached content.
