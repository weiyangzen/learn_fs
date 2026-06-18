# File Research: sources/cow-pools/bcachefs-tools/c_src/libbcachefs.h

- Header for userspace libbcachefs helper structs.
- Defines `bch_opt_strs` union keyed by option id or named option fields generated from `BCH_OPTS`.
- Declares option cleanup/parsing helpers.
- Defines `format_opts`, `dev_opts`, `dev_opts_list`, and default device options.
