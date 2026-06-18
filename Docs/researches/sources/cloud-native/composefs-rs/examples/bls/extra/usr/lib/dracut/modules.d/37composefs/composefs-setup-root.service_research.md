# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs systemd unit that runs `composefs-setup-root` during BLS boot when the kernel command line contains `composefs`.

Important APIs/types/functions: `[Unit]` with `ConditionKernelCommandLine=composefs`, `After/Requires=sysroot.mount`, `Before=initrd-root-fs.target` and `initrd-switch-root.target`; `[Service]` one-shot `ExecStart=/usr/bin/composefs-setup-root`.

Control flow: systemd in the initramfs starts this after `/sysroot` is mounted and before switch-root, isolating to emergency target on failure.

State/persistence: the unit itself is packaged into initramfs; runtime mount/sysroot state is modified by the setup binary.

Dependencies/integration: depends on systemd initrd, dracut module installation, `composefs-setup-root`, and kernel cmdline.

Risks/test signals: ordering is critical; running too early or too late can leave an unusable root. VM boot and `test.sh` exercise the behavior.
