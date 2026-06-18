# sources/distributed-fs/ceph-client/scripts/dummy-tools/dummy-plugin-dir/include/plugin-version.h

Purpose: Empty placeholder header used by dummy compiler tooling so Kconfig checks for GCC plugin header availability can succeed.

Important APIs/types: None; the file has zero lines.

Control flow: No logic. Its existence is the behavior.

State/persistence: None.

Dependencies/integration: Returned indirectly by `scripts/dummy-tools/gcc -print-file-name=plugin`, which points at `dummy-plugin-dir`; Kconfig tests for `include/plugin-version.h`.

Risks: If removed or relocated, `HAVE_GCC_PLUGINS`/`GCC_PLUGINS` visibility tests under dummy tools may fail. Because it is empty, it cannot support actual plugin compilation.

Test signals: `make CROSS_COMPILE=scripts/dummy-tools/ oldconfig` should see the path as existing for plugin capability probes.
