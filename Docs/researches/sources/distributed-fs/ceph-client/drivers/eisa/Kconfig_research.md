# sources/distributed-fs/ceph-client/drivers/eisa/Kconfig

## Purpose
This Kconfig file defines the kernel configuration surface for legacy EISA bus support, including core EISA bus enumeration, VLB priming, PCI/EISA bridges, virtual root probing, and the optional EISA device-name database.

## Important APIs, types, and functions
The important symbols are `HAVE_EISA`, `EISA`, `EISA_VLB_PRIMING`, `EISA_PCI_EISA`, `EISA_VIRTUAL_ROOT`, and `EISA_NAMES`. There are no runtime functions in this file, but these symbols control which C files and generated headers are built.

## Control flow
`EISA` is a menuconfig gated by architecture-provided `HAVE_EISA`. `EISA_PCI_EISA` depends on PCI and excludes PARISC, while `EISA_VIRTUAL_ROOT` is limited to x86 EISA systems. `EISA_NAMES` enables a generated device-name table. Defaults favor legacy usability where EISA is already enabled.

## State and persistence behavior
The file has build-time state only. It changes compiled code and generated tables but has no runtime persistence.

## Dependencies and integration points
It integrates with Kbuild in the sibling Makefile and with architecture/platform code that selects `HAVE_EISA`. `EISA_NAMES` drives generation and inclusion of `devlist.h` from `eisa.ids`.

## Risks and edge cases
The virtual-root option is intentionally x86-only because forced probing on other architectures may crash. Enabling EISA_NAMES increases image size temporarily during boot. Disabling PCI bridge or virtual-root support can leave an EISA system without a root device to enumerate.

## Test signals
Relevant validation is Kconfig matrix coverage: `EISA=y/n`, x86/non-x86, PCI bridge enabled/disabled, virtual root enabled/disabled, and `EISA_NAMES` enabled/disabled with successful builds.
