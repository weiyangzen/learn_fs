# sources/cloud-native/overlayfs-tools/main.c

Purpose: command-line front end for the `overlay` utility, validating arguments and invoking diff/vacuum/merge/deref actions.

Important APIs/types/functions: `print_help`, `starts_with`, `is_mounted`, `check_mounted`, `directory_exists`, `directory_create`, `check_xattr_trusted`, and `main`; global flags `verbose`, `brief`, `ignore`, `force`, and `use_rsync`.

Control flow: parses lower/upper/mount/new-dir/options, resolves real paths, verifies lower and upper directories, checks ability to set `trusted.overlay.*` xattrs, warns/refuses if the overlay appears mounted for mutating actions, then runs the selected action. Mutating actions create a temporary shell script and either tell the user to run it or execute/delete it when `--force` is set.

State and persistence: may create new lower/upper backup directories, create generated shell scripts, and with force execute commands that mutate lower/upper trees. It writes a temporary xattr probe file in upperdir.

Dependencies/integration: calls `logic.c` actions and `sh.c` script generation; relies on `/proc/mounts` parsing and trusted xattr support.

Risks: mount detection uses string prefix matching and has complex negation that can false-positive/negative. Generated script execution uses `system`. Trusted xattr requirement means root or equivalent capability is needed even for diff.

Test signals: Meson tests cover diff variants; manual tests should cover force execution, mounted checks, new-dir backup behavior, and deref requirements.
