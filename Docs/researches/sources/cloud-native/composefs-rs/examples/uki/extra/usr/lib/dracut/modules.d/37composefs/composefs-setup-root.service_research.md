# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: UKI copy of the initramfs systemd service that runs `composefs-setup-root`.

Important APIs/types/functions: same unit contract as BLS: `ConditionKernelCommandLine=composefs`, requires `sysroot.mount`, runs before initrd root/switch-root targets, and executes `/usr/bin/composefs-setup-root`.

Control flow: starts only when composefs cmdline is present during initrd boot.

State/persistence: packed into the UKI initramfs.

Dependencies/integration: dracut module install, systemd initrd, and composefs setup binary.

Risks/test signals: ordering and failure isolation are boot-critical; tested by VM boot.
