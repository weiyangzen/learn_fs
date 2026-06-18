# sources/cloud-native/ostree/src/switchroot/ostree-system-generator.c

Purpose: small systemd generator frontend that delegates actual unit generation to libostree private command code.

Important APIs/functions: `main()` accepts either no arguments or the three systemd generator directories, assigns `arg_dest` and `arg_dest_late`, then calls `ostree_cmd__private__()->ostree_system_generator(arg_dest, NULL, arg_dest_late, &error)`.

Control flow: validate argc, map generator args, invoke private implementation, print fatal error on failure, exit success otherwise.

State/persistence: this frontend itself writes no files directly, but the private generator writes systemd units into the generator output directories.

Dependencies/integration: depends on `ostree-cmd-private.h`, libglnx/GError handling, and the systemd generator calling convention. It is tied to `/boot` and `/var` mount behavior moved out of prepare-root.

Risks: argument validation is strict: any argc other than 1 or 4 fails. Actual generator behavior is hidden in libostree private API, so frontend tests only validate delegation.

Test signals: `tests-unit-container/test-prepare-root.sh` asserts prepare-root does not mount `/boot`, explicitly pointing to generator responsibility.
