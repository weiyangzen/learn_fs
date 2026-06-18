# sources/distributed-fs/ceph-client/lib/kunit/hooks.c

Purpose: provides built-in KUnit hook state even when KUnit core is built as a module.

Important APIs/state: defines and exports static key `kunit_running` and global `struct kunit_hooks_table kunit_hooks`.

Control flow: no active runtime logic; exported symbols are initialized statically and later manipulated by KUnit core/hook installation.

State and persistence: `kunit_running` is a static branch indicating active KUnit execution; `kunit_hooks` stores function pointers for failure and static stub callbacks.

Dependencies and integration: includes `kunit/test-bug.h`, uses static keys and export macros. Built through Makefile as built-in when KUnit is enabled.

Risks: consumers must tolerate NULL hook function pointers before installation; static branch state must be toggled consistently by core test execution.

Test signals: KUnit current-test failure tests, static stub tests, and build/link tests with modular KUnit.
