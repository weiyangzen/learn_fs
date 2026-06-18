# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs service for running composefs setup in unified-secureboot UKIs.

Important APIs/types/functions: systemd initrd unit with composefs cmdline condition, sysroot dependency, initrd target ordering, emergency failure isolation, and one-shot setup execution.

Control flow: activated in signed UKI initramfs before switch-root.

State/persistence: embedded in generated signed UKI.

Dependencies/integration: dracut module installer and composefs setup binary.

Risks/test signals: failure can break Secure Boot boot chain; `run` exercises boot.
