# sources/distributed-fs/glusterfs/xlators/meta/src/options-dir.c

Purpose: implements the virtual `options` directory beneath each xlator entry, dynamically listing every key in the target translator's options dictionary.

Important APIs/types/functions: `options_dir_fill()` allocates an array of `struct meta_dirent` sized by `xl->options->count`. `dict_key_add()` fills each entry with a duplicated key name, regular-file type, and `meta_option_file_hook`. `meta_options_dir_hook()` propagates parent xlator context and attaches `options_dir_ops`.

Control flow: lookup or readdir of `options` first installs `options_dir_ops`. Readdir calls `options_dir_fill()` via the default directory path, then each returned dirent can be looked up as an option file.

State and persistence behavior: dynamic dirents are generated from the live options dict and cached per directory fd until release. The directory itself persists no state.

Dependencies and integration points: depends on Gluster dict iteration, `GF_CALLOC`, `gf_strdup`, `meta_option_file_hook`, and the xlator context installed by `xlator-dir.c`.

Risks and edge cases: allocation size uses the dict count and assumes `dict_foreach()` visits exactly that many entries. Option mutations while a directory fd is open can make listings stale. `dict_key_add()` does not handle `gf_strdup()` failure per entry.

Test signals: readdir on xlator `options`, lookup/read each generated option file, memory cleanup on releasedir, and option dictionary mutation followed by reopen.
