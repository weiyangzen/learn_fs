# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/prom.c

Purpose: detects XWAY-family SoC IDs and maps them to human-readable names, Lantiq type constants, and DT compatible strings.

Important APIs/functions: `ltq_soc_detect`.

Control flow: reads `LTQ_MPS_CHIPID`, extracts part number and revision, formats `rev_type`, and switches over many Danube/Twinpass/Amazon SE/AR9/GR9/VR9/VRX220/AR10/GRX390 part IDs. Amazon SE panics if built with PCI.

State and persistence: fills the supplied `struct ltq_soc_info`; no persistent state beyond caller storage.

Dependencies and integration: called by generic Lantiq `prom_init()`; depends on SoC ID macros and MMIO register helpers from `lantiq_soc.h`.

Risks: unknown IDs call `unreachable()`. Multiple GR/VR variants share compatible strings and type constants, so downstream code must tolerate family grouping.

Test signals: boot SoC name/revision string for each supported chip ID and correct machine compatibility branches in `xway/sysctrl.c`.
