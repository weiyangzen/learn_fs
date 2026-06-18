# sources/distributed-fs/ceph-client/drivers/char/agp/Kconfig

## Purpose
This Kconfig file defines AGPGART support and chipset-specific AGP bridge drivers.

## Important APIs, Types, and Functions
The main symbol is `AGP`, a tristate `/dev/agpgart` option depending on PCI and one of Alpha, PA-RISC, PowerPC, or x86. Chipset symbols include `AGP_ALI`, `AGP_ATI`, `AGP_AMD`, `AGP_AMD64`, `AGP_INTEL`, `AGP_NVIDIA`, `AGP_SIS`, `AGP_SWORKS`, `AGP_VIA`, `AGP_PARISC`, `AGP_ALPHA_CORE`, `AGP_UNINORTH`, and `AGP_EFFICEON`. `INTEL_GTT` is an internal tristate selected by Intel AGP support.

## Control Flow
Selecting `AGP` enables the generic backend. Selecting chipset options causes matching PCI/platform bridge drivers to build and register with the generic AGP backend.

## State and Persistence Behavior
Configuration state controls whether `/dev/agpgart`, generic AGP memory management, and chipset-specific GART setup are built.

## Dependencies and Integration Points
The options reflect architecture and chipset restrictions: many legacy chipsets are x86_32-only, AMD64 uses AMD northbridge support, Alpha and PA-RISC use architecture-specific backends, and Intel selects `INTEL_GTT`.

## Risks
AGP is legacy but low-level: enabling unsupported chipset drivers can affect aperture setup and DMA mappings. `AGP_AMD64` supports a try-unsupported path at runtime, but Kconfig cannot validate actual bridge/NB compatibility.

## Test Signals
Kconfig build matrix across supported architectures, ensuring only valid chipset options appear and module names match Makefile outputs.
