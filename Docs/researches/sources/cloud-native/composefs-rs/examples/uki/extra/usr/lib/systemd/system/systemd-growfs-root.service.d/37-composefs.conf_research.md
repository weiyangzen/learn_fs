# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: UKI copy of the growfs override that targets `/sysroot`.

Important APIs/types/functions: clears `ExecStart` and sets `/usr/lib/systemd/systemd-growfs /sysroot`.

Control flow: systemd drop-in redirects root growfs.

State/persistence: persistent unit override in the image.

Dependencies/integration: systemd and composefs backing sysroot layout.

Risks/test signals: incorrect target breaks disk growth or mutates the composed root.
