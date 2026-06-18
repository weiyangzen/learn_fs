# sources/cloud-native/ostree/tests/test-remotes-config-dir.js

## Purpose
This GJS test validates the libostree `Ostree.Repo` `remotes_config_dir` behavior, including reading external remote config files, deciding where new remotes are written, deleting external remotes, and replacing remote options.

## Important APIs, Types, And Functions
It imports `GLib`, `Gio`, and `OSTree`. Key APIs include `GLib.KeyFile`, `OSTree.Repo({path, remotes_config_dir})`, `repo.create`, `repo.open`, `remote_list`, `remote_add`, `remote_delete`, `copy_config`, `write_config`, `reload_config`, `remote_get_gpg_verify`, and `remote_change` with `OSTree.RepoRemoteChange.REPLACE`.

## Control Flow
The script creates `remotes.d/foo.conf`, opens a repo configured with that directory, and confirms `foo` is visible. It adds `bar` and confirms it is stored in the main config rather than `remotes.d`. Deleting `foo` removes its config file. After enabling `core.add-remotes-config-dir`, adding `baz` writes `baz.conf`. It verifies changing main-config remote `bar` through `write_config()` succeeds, while changing config-dir remote `baz` through `write_config()` fails with `G_IO_ERROR_EXISTS`. It then replaces a missing remote and existing config-dir and main-config remotes, confirming old `branches` options are removed.

## State And Persistence
State is split between the main repo config and files under `remotes.d/*.conf`. The test checks actual file existence and key file contents to validate persistence location.

## Dependencies And Integration Points
This integrates GObject introspection bindings, libostree remote config loading, config-dir precedence, config write safety, and remote replacement semantics.

## Risks
The main risks are accidentally writing external remotes into the wrong config, allowing `write_config()` to overwrite config-dir-owned remotes, or retaining stale options during replace. GPG support is optional for one check and produces a TAP skip when unsupported.

## Test Signals
Nine TAP-style printed `ok` lines cover reading, adding, deleting, write-config behavior, replace of missing remote, and replace in both config-dir and main config.
