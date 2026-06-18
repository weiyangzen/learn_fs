# sources/cloud-native/ostree/man/ostree-admin-switch.xml

Purpose: documents `ostree admin switch`, which changes the tracked ref from the current remote and deploys if changed.

Important APIs/types: required `REF`; options `--reboot/-r`, `--kexec/-k`, and `--os="STATEROOT"`.

Control flow: updates origin tracking to a different ref, performs upgrade-like deploy while preserving OS state, and can reboot or kexec after deployment.

State and persistence: mutates origin/ref tracking, deployment state, and potentially boot/runtime transition.

Dependencies and integration: integrates remotes, upgrade code paths, stateroot selection, bootloader, and reboot/kexec mechanisms.

Risks and test signals: risks include switching across incompatible refs, reboot/kexec side effects, and preserving state correctly. Signals are switch tests, origin update checks, and post-switch status output.
