# sources/distributed-fs/ceph-client/scripts/gdb/linux/__init__.py

Purpose: Package initializer for the Linux GDB Python helpers.

Important APIs/types: None; contains only a comment noting no initialization work.

Control flow: Importing `linux` performs no side effects from this file.

State/persistence: None.

Dependencies/integration: Allows helper modules to be imported as `linux.<module>`.

Risks: No direct risk; initialization is intentionally left to individual modules.

Test signals: `import linux` should succeed when the package path is configured.
