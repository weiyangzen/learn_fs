## sources/cloud-native/containers-storage/pkg/homedir/homedir_test.go

Purpose: basic tests for platform home directory lookup and shell shortcut string.

Important APIs/types/functions: `TestGet` and `TestGetShortcutString`.

Control flow: calls `Get`, asserts non-empty absolute path, then calls `GetShortcutString` and asserts non-empty string.

State and persistence: reads environment/user lookup only.

Dependencies and integration points: smoke coverage for platform-specific homedir implementations.

Risks: tests do not cover XDG data/cache/config/runtime helpers, sticky runtime behavior, permissions, or symlink resolution.

Test signals: weak smoke signal; local execution blocked by missing Go toolchain.
