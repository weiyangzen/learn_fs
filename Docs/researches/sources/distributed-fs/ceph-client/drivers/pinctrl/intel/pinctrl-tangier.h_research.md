# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.h

Purpose: Defines the public data contract for Intel Tangier pinctrl platform data and declares the reusable probe entry implemented in `pinctrl-tangier.c`.

Important APIs/types/functions: Defines `TNG_FAMILY_NR`, `TNG_FAMILY_LEN`, `struct tng_family`, `TNG_FAMILY()`, `TNG_FAMILY_PROTECTED()`, `struct tng_pinctrl`, and `devm_tng_pinctrl_probe()`. `struct tng_family` maps pin ranges to MMIO family slots and can mark a family protected. `struct tng_pinctrl` packages the pinctrl descriptor, functions, groups, pins, and family list consumed by the probe helper.

Control flow: The header has no executable path. SoC-specific files instantiate const `struct tng_pinctrl` objects and expose them as match data. `devm_tng_pinctrl_probe()` duplicates that data, fills runtime MMIO fields, and registers the pin controller.

State and persistence: No direct mutable state exists in the header. Its structures define which state the implementation persists at runtime: copied family records with `regs`, a raw spinlock, and the registered `pinctrl_dev`. The protected bit is part of the persistent platform policy for inaccessible pin families.

Dependencies and integration points: Includes pinctrl core types and Intel shared group/function definitions from `pinctrl-intel.h`. It is the boundary between Tangier SoC data files and the common Tangier implementation.

Risks: The constants encode the MMIO family stride; an incorrect `TNG_FAMILY_LEN` or `barno` in users would make all register accesses land in the wrong window. Family ranges must be non-overlapping and cover every advertised pin that can be touched by groups. Protected families must be set for firmware-owned banks or the driver can attempt illegal MMIO operations.

Test signals: Build all Tangier SoC users, inspect match data for family coverage, probe on hardware or emulation, and verify protected families are reported as unavailable through debugfs and pinconf/pinmux operations.
