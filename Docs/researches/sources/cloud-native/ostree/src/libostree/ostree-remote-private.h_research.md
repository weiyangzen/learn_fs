# sources/cloud-native/ostree/src/libostree/ostree-remote-private.h

## Purpose
This private header defines the concrete `OstreeRemote` structure and internal constructors used by repository configuration code.

## Important APIs, State, and Integration
`struct OstreeRemote` contains an atomic `ref_count`, display `name`, optional `refspec_name` for dynamic remotes inheriting from a static remote, keyfile `group`, keyring filename, optional config `GFile`, and `GKeyFile *options`. Internal constructors are `ostree_remote_new()`, `ostree_remote_new_dynamic()`, and `ostree_remote_new_from_keyfile()`.

## Dependencies, Risks, and Tests
The header depends on GLib/GIO, libglnx, public `ostree-remote.h`, and `ostree-types.h`. Integration points are repo remote loading, dynamic remote creation, keyring selection, and URL lookup. Risks are representation leakage inside libostree, especially around whether `name` or `refspec_name` should be used for config groups and keyrings. Tests should cover static and dynamic remote construction and keyfile group parsing.
