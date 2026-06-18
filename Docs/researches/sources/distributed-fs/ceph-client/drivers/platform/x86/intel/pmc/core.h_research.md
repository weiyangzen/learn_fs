# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.h

Purpose: central header for the Intel PMC Core driver. It defines register offsets, device IDs, shared constants, core data structures, platform hooks, exported platform data, and debugfs helper macros used by all PMC platform files.

Important APIs/types/functions: `struct pmc_bit_map` names bits and optionally supplies blocker stride metadata. `struct pmc_reg_map` is the central platform contract for register offsets, bit maps, LPM layout, S0ix blocker layout, telemetry GUIDs, and counter units. `struct pmc_info` maps SSRAM device IDs to regmaps. `struct pmc` stores one controller's MMIO base, regmap, LPM requirements, saved LTR ignore state, and enabled modes. `struct pmc_dev` stores the driver instance and up to `MAX_NUM_PMC` controllers. `struct pmc_dev_info` is the CPU/platform descriptor with init/suspend/resume/sub-requirement callbacks. `pmc_for_each_mode()` iterates enabled LPM modes, and `DEFINE_PMC_CORE_ATTR_WRITE()` builds writable debugfs file operations.

Control flow: platform `.c` files fill `pmc_dev_info`, `pmc_reg_map`, and `pmc_info` data declared here; `core.c` consumes those at probe and runtime. Legacy platforms rely on a single `.map`, while SSRAM platforms set `.regmap_list` and telemetry callbacks. The header's offsets and device IDs determine which MMIO regions are mapped and which LTR/LPM/debugfs controls are exposed.

State and persistence: the header itself has no state, but defines all persistent in-memory state held for module lifetime. Register macros encode hardware ABI and must remain stable for the matching silicon generation.

Dependencies and integration points: includes ACPI bits and platform-device types and forward-declares `struct telem_endpoint` from PMT telemetry. Externs tie together SPT/CNP/ICL/TGL/ADL/MTL/ARL/LNL/PTL/WCL platform descriptors, and function declarations tie platform files back to `core.c`.

Risks: a wrong offset, counter step, `ltr_ignore_max`, device ID, or map count silently corrupts debug output or hardware control. `pmc_bit_map.blk` has meaning only for blocker-style paths; maps used in both bit display and blocker paths must keep that field consistent. Cross-file externs require link-time consistency as newer files reuse MTL/PTL maps.

Test signals: build/link coverage catches missing extern definitions, but not incorrect values. Runtime signals are correct debugfs file presence, sane LTR and LPM output on each supported CPU, successful SSRAM matching by device ID, and absence of invalid memory accesses when optional maps are NULL.
