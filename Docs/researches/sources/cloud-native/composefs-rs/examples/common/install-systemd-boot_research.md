# sources/cloud-native/composefs-rs/examples/common/install-systemd-boot

Purpose: prepares an EFI System Partition tree with systemd-boot for example images.

Important APIs/types/functions: creates `tmp/efi/loader`, writes `loader.conf`, creates `EFI/BOOT` and `EFI/systemd`, and copies `systemd-bootx64.efi` to both vendor and fallback paths.

Control flow: straight-line shell script that populates the temporary ESP before repartitioning.

State/persistence: writes files under `tmp/efi`.

Dependencies/integration: depends on systemd-boot binary path and is consumed by `run-repart` partition definitions.

Risks/test signals: x86_64-specific paths and binary name; missing package breaks image build.
