# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/hooks/composefs

Purpose: mkinitcpio late hook that runs composefs root setup when `composefs` is present on the kernel command line.

Important APIs/types/functions: `run_latehook`, `getarg composefs`, and `/usr/bin/composefs-setup-root --sysroot /new_root`.

Control flow: the late hook exits silently without the cmdline flag; otherwise it invokes setup against mkinitcpio's `/new_root`.

State/persistence: no persistent state itself; mutates the initramfs mount tree at boot.

Dependencies/integration: depends on mkinitcpio ash runtime, `getarg`, and installed `composefs-setup-root`.

Risks/test signals: assumes `/new_root` semantics and command availability. Boot tests for mkinitcpio/Arch-like paths are the signal.
