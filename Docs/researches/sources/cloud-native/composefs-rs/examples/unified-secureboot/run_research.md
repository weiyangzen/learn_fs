# sources/cloud-native/composefs-rs/examples/unified-secureboot/run

Purpose: manual QEMU runner for unified-secureboot images, optionally enabling Secure Boot using generated/custom OVMF variable templates.

Important APIs/types/functions: detects `secureboot/`, invokes `virt-fw-vars` with PK/KEK/db certs, prepares `qemu_args`, and runs `qemu-system-x86_64` with virtio disk and optional secure pflash.

Control flow: if secureboot directory exists, builds or reuses a VARS template, copies it for a fresh run, and enables SMM/secure pflash; otherwise uses plain OVMF BIOS path. Then launches QEMU headless with `fedora-unified-secureboot-efi.qcow2`.

State/persistence: writes `VARS_CUSTOM.secboot.fd.template` and per-run `VARS_CUSTOM.secboot.fd`.

Dependencies/integration: depends on QEMU/KVM, edk2 OVMF secureboot paths, `virt-fw-vars`, and generated qcow2 image.

Risks/test signals: firmware paths and QEMU machine version are host-specific. This is the direct manual signal that signed UKIs boot under Secure Boot.
