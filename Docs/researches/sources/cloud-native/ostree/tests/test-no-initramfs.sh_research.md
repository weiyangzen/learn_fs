<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-no-initramfs.sh -->
# sources/cloud-native/ostree/tests/test-no-initramfs.sh

## Purpose
`test-no-initramfs.sh` verifies deployment behavior for OS trees without initramfs images across supported boot file layouts.

## Important APIs, Types, And Functions
The script uses `setup_os_repository "archive-z2" "uboot"`, `ostree admin deploy`, `ostree admin upgrade`, bootloader entry inspection, helper `pull_test_tree`, helper `get_key_from_bootloader_conf`, and loops over layouts under `/usr/lib/modules`, `/usr/lib/ostree-boot`, and `/boot`.

## Control Flow
It first deploys a tree and checks the generated bootloader entry has the expected root argument and no `init=` entry. It then creates additional commits with kernels and no initramfs in each layout, upgrades/deploys them, and verifies bootloader entries and boot file installation stay correct.

## State And Persistence
State is a temporary sysroot, OS repository, bootloader entry files, deployment directories, and generated OS commit trees. Boot artifacts are persisted under the temporary sysroot.

## Dependencies And Integration Points
The test integrates admin deploy/upgrade code, bootloader config generation, kernel/initramfs discovery, u-boot layout handling, and OS repository fixture helpers.

## Risks And Test Signals
The risk is bootloader generation assuming an initramfs exists or losing kernel args. Passing signals include deployment success, no `init=` line when absent, correct root argument, and correct behavior across all tested boot layouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-no-initramfs.sh -->
