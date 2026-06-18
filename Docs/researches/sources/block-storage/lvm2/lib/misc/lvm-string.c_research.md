# File Research: sources/block-storage/lvm2/lib/misc/lvm-string.c

This file implements string formatting, name validation, reserved LV name detection, DM UUID construction, suffix removal, and line splitting.

Main APIs:
- `emit_to_buffer()`: safe append-style `vsnprintf()` wrapper.
- `validate_tag()`, `validate_name()`, `validate_name_detailed()`.
- `copy_systemid_chars()`.
- `apply_lvname_restrictions()`, `is_reserved_lvname()`, `is_component_lvname()`.
- `build_dm_uuid()`.
- `first_substring()`, `drop_lvname_suffix()`, `split_line()`.

Behavior:
- Valid LVM names allow alnum plus `.`, `_`, `-`, `+`, reject empty, leading hyphen, `.`/`..`, invalid chars, and length over `NAME_LEN`.
- Tags allow a broader set including `/`, `=`, `!`, `:`, `&`, `#`.
- Reserved LV prefixes include `pvmove` and `snapshot`.
- Reserved component strings include `_cdata`, `_cmeta`, `_corig`, `_cpool`, `_cvol`, `_wcorig`, `_mimage`, `_mlog`, `_rimage`, `_rmeta`, `_tdata`, `_tmeta`, `_vdata`, `_imeta`, `_iorig`; additional reserved strings include `_pmspare`, `_vorigin`.
- `build_dm_uuid()` chooses implicit layer suffixes for internal LVs such as `real`, `pool`, `tdata`, `tmeta`, `vdata`, `cvol`.

Dependencies:
- Metadata LV classification helpers, display/logging, libdevmapper UUID builder.

Correctness notes:
- DM UUID layer suffix choices must match activation/dev-manager code comments.
- `copy_systemid_chars()` skips invalid characters and truncates to `NAME_LEN`.

Risks:
- Reserved substring detection starts at first `_`, so naming behavior depends on underscore placement.
- `split_line()` mutates the input buffer.
