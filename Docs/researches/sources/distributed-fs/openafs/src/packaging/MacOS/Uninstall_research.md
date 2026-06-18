# sources/distributed-fs/openafs/src/packaging/MacOS/Uninstall

Purpose: Perl uninstaller for Mac OpenAFS packages, adapted from Apple's devtools uninstaller.

Important APIs/types/functions: `main`, `remove_generated_files`, `remove_main_packages`, `remove_generated_directories`, `add_directory_to_tree`, `remove_empty_directories`, `remove_a_file`, `remove_a_dir`, `remove_package_receipts`, `maybe_remove_ds_store`, and printing/spinner helpers. Package names include OpenAFS and debug variants. Generated config files under `/var/db/openafs/etc` are explicitly removed.

Control flow: defaults package directory from script location, removes generated files, scans package BOMs from old `/Library/Receipts` or new `/var/db/receipts`, queues files/directories/receipts for deletion, then runs a single privileged `osascript` shell command to remove them. It uses `lsbom` to enumerate package files and directories and attempts to remove empty directories bottom-up.

State and persistence: destructive filesystem changes: removes package files, generated OpenAFS config/cache metadata, empty dirs, and package receipts. Arrays `@rmfiles`, `@rmdirs`, and `@rmpkg` accumulate removals.

Dependencies/integration: depends on Perl, `File::Basename`, `/usr/bin/lsbom`, `/bin/rm`, `/bin/rmdir`, `osascript`, macOS receipt layout, and package BOM metadata.

Risks and test signals: command construction interpolates file paths into an AppleScript shell string, so spaces/quotes are risky. It can remove user config files listed in `@gen_files`. Dry-run mode variables exist but are not exposed via CLI. Test in a disposable system image with package receipts and generated files.
