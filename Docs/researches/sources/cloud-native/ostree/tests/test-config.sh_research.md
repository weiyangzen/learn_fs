# sources/cloud-native/ostree/tests/test-config.sh

Purpose: validates `ostree config get/set/unset` behavior, grouped remote keys, argument errors, and value validation.

Important APIs/functions: `setup_test_repository bare`, `ostree remote add --set`, `ostree config get`, `set`, `unset`, `--group`, `--` separator, and config file assertions.

Control flow: creates remotes with custom keys, reads core and remote values, verifies too-many-argument errors, updates core and remote values, unsets keys including missing/remote groups, validates missing-key errors, and checks `core.min-free-space-size` rejects invalid values while accepting `100MB`.

State/persistence: mutates `repo/config` and remote entries. Dependencies include GLib keyfile error wording and config validation code.

Integration/risk/test signals: protects CLI config editing used by scripts and admins. Risks are exact keyfile error text and quoting/group syntax. TAP ok lines cover get, set, unset, and validation.
