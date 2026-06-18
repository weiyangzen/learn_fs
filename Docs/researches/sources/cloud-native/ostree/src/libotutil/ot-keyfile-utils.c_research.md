# sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.c

## Purpose
Provides helper functions for reading `GKeyFile` values with defaults, parsing booleans/tristates, reading string lists with flexible separators, and copying groups between key files.

## Important APIs, Types, And Functions
Key functions are `ot_keyfile_get_boolean_with_default`, `_ostree_parse_boolean`, `_ostree_parse_tristate`, `ot_keyfile_get_tristate_with_default`, `ot_keyfile_get_value_with_default`, `ot_keyfile_get_value_with_default_group_optional`, `ot_keyfile_get_string_list_with_separator_choice`, `ot_keyfile_get_string_list_with_default`, and `ot_keyfile_copy_group`. Internal `is_notfound` identifies missing key/group errors.

## Control Flow
Defaulted getters call the corresponding `GKeyFile` getter, substitute defaults on missing key/group, and propagate parse or other errors. Boolean parsing accepts `yes/no`, `true/false`, and `1/0`. Tristate parsing accepts `maybe` or boolean values. Separator-choice list parsing detects which separator from a provided set appears in a raw value, errors if multiple separator types appear, treats no separator as a one-element list, and otherwise delegates to `g_key_file_get_string_list` with the selected separator.

## State And Persistence Behavior
No persistent state is written. The string-list getter mutates the `GKeyFile` list separator setting, which can affect later reads using the same keyfile.

## Dependencies And Integration Points
Depends on GLib `GKeyFile`, libglnx errors, and `OtTristate` from the header. Used by prepare-root config parsing, repo config parsing, and CLI/config utilities.

## Risks
`ot_keyfile_get_value_with_default` treats both missing group and missing key as default, while the group-optional wrapper is partly redundant because the inner function already handles group-not-found. `g_key_file_set_list_separator` has keyfile-wide effect. Separator-choice detection only checks presence, not escaping or list syntax semantics.

## Test Signals
Tests should cover missing key/group defaults, invalid boolean/tristate values, `maybe`, separator choice with no/one/multiple separator types, default string lists, group copy behavior, and keyfile separator side effects.
