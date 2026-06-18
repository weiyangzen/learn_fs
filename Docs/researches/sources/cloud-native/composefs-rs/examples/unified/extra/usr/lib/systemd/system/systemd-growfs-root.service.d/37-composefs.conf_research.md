# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: growfs root service override for unified composefs images.

Important APIs/types/functions: replaces default `ExecStart` with `systemd-growfs /sysroot`.

Control flow: applied when systemd starts growfs service.

State/persistence: persistent systemd drop-in.

Dependencies/integration: composefs sysroot layout.

Risks/test signals: wrong target can fail disk growth or mutate incorrect filesystem.
