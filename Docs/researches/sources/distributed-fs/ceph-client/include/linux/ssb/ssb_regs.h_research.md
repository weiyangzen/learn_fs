<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h

Purpose: Provides the SSB physical address map, PCI config register offsets, core enumeration constants, target/initiator state registers, identification fields, SPROM layout constants, board flags, country codes, and address-match masks.

Important APIs/types/functions: `SSB_*` address constants such as `SSB_ENUM_BASE`, `SSB_CORE_SIZE`, `SSB_MAX_NR_CORES`, PCI config offsets, backplane register offsets (`SSB_TMSLOW`, `SSB_TMSHIGH`, `SSB_IDLOW`, `SSB_IDHIGH`, etc.), SPROM size/base/revision constants, SPROM field masks, board flag masks, country-code enum, and `SSB_ADM_*` address-match masks.

Control flow: No executable control flow. The constants drive enumeration, register decode, SPROM parsing, reset/enable sequences, interrupt routing, and address-window calculations in SSB implementations.

State and persistence behavior: Describes hardware register and SPROM persistent data layout. The header itself stores no state.

Dependencies: Expected to be included by SSB core headers and C files; assumes kernel integer types are available through includers.

Integration points: SSB bus enumeration, PCI and SoC register programming, SPROM parsing, board quirk selection, and memory/flash window mapping.

Risks: Incorrect constants corrupt hardware access. SPROM fields are revision-specific and must be parsed with the right base/size/mask. `SSB_MAX_NR_CORES` depends directly on enumeration range constants.

Test signals: Register decode tests against known chip dumps, SPROM parsing fixtures for revisions 1/4/10/11, board flag quirk tests, and enumeration count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h -->
