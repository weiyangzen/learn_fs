# File Research: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.c

- Small userspace support file for option string handling.
- Frees all strdup’d option strings in `bch_opt_strs`.
- Parses deferred option strings into a `bch_opts` struct, tolerating options that require an open filesystem but dying on other parse errors.
