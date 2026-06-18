# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: overrides `systemd-growfs-root.service` to grow `/sysroot` instead of the composed read-only `/` in BLS composefs systems.

Important APIs/types/functions: systemd drop-in clears `ExecStart=` and replaces it with `/usr/lib/systemd/systemd-growfs /sysroot`.

Control flow: systemd merges the drop-in when starting growfs, redirecting the grow operation to the backing writable sysroot partition.

State/persistence: persistent service override in the image; runtime effect changes filesystem growth target.

Dependencies/integration: depends on systemd unit override semantics and `/sysroot` being the backing filesystem.

Risks/test signals: if `/sysroot` is absent or renamed, growfs fails or grows the wrong filesystem. VM boot and persistence tests are indirect signals.
