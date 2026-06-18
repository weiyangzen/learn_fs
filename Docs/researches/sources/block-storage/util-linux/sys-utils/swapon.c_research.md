# File Research: sources/block-storage/util-linux/sys-utils/swapon.c

This file implements `swapon(8)`: listing active swap, enabling individual swap devices/files, enabling all fstab swap entries, resolving labels/UUIDs, parsing swap options, and validating swap headers before calling the `swapon(2)` syscall.

Output mode is built around `struct swapon_ctl`, the `infos[]` column table, and libsmartcols. `display_summary()` preserves the deprecated `-s` tabular format from `/proc/swaps`; `show_table()` and `add_scols_line()` implement `--show`, optional raw/no-heading/byte output, annotations, and optional UUID/LABEL lookup through `get_swap_prober()`.

Activation preflight is centered on `swapon_checks()`. It opens the target, warns about insecure permissions and non-root-owned regular files, rejects sparse regular swap files, obtains block-device or file size, reads up to `MAX_PAGESIZE`, detects swap or suspend signatures, compares swap-header page size to the system page size, optionally runs `mkswap` through `swap_reinitialize()`, and rewrites obsolete software-suspend signatures through `swap_rewrite_signature()`. `swap_get_size()` handles byte-swapped swap headers, and `swap_get_info()` preserves label/UUID when reinitializing.

`do_swapon()` resolves noncanonical specs through `mnt_resolve_spec()`, runs the checks, constructs kernel flags from priority and discard policy, then calls `swapon(path, flags)`. Discard handling accepts whole-device discard, `once`, `pages`, or both policy bits collapsed to `SWAP_FLAG_DISCARD` for the kernel. Label and UUID activation are wrappers around `mnt_resolve_tag()`.

`parse_options()` understands fstab/`-o` options relevant to swap: `nofail`, `discard[=once|pages]`, and `pri=<n>`. `swapon_all()` iterates swap fstab entries with `match_swap()`, skips `noauto`, merges per-entry options over global defaults, resolves tags to real devices, skips already-active swaps, honors `nofail` for missing/inaccessible devices, and enables each remaining swap.

`main()` initializes locale, libmount debug state, the global cache, parses options, enforces incompatible option groups, and dispatches to summary, show-only default output, `--all`, label/UUID lists, and positional specs. It frees the shared libmount tables and cache before returning the ORed syscall/status result.
