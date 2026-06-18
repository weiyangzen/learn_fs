# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs service for composefs root setup in unified UKIs.

Important APIs/types/functions: composefs cmdline condition, `sysroot.mount` dependency, ordering before initrd root/switch-root targets, one-shot `ExecStart=/usr/bin/composefs-setup-root`.

Control flow: systemd initrd starts it when composefs boot is requested.

State/persistence: embedded in generated UKI.

Dependencies/integration: dracut, systemd, and setup binary.

Risks/test signals: unit ordering controls root pivot correctness; VM tests validate.
