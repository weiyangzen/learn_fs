# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: growfs override for unified-secureboot images, targeting `/sysroot`.

Important APIs/types/functions: resets `ExecStart` then runs `systemd-growfs /sysroot`.

Control flow: systemd applies it when starting root growfs.

State/persistence: persistent unit drop-in.

Dependencies/integration: systemd and composefs sysroot layout.

Risks/test signals: backing partition must be mounted at `/sysroot`; VM boot validates.
