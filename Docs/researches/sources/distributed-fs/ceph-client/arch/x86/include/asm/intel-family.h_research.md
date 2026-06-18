<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h

## Purpose
Intel CPU family/model ID catalog used by feature quirks, drivers, mitigations, and platform matching. The header is 227 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_FAMILY_H`; `#define IFM(_fam, _model) VFM_MAKE(X86_VENDOR_INTEL, _fam, _model)`; `#define INTEL_ANY IFM(X86_FAMILY_ANY, X86_MODEL_ANY)`; `#define INTEL_FAM5_START IFM(5, 0x00) /* Notational marker, also P5 A-step */`; `#define INTEL_PENTIUM_75 IFM(5, 0x02) /* P54C */`; `#define INTEL_PENTIUM_MMX IFM(5, 0x04) /* P55C */`; `#define INTEL_QUARK_X1000 IFM(5, 0x09) /* Quark X1000 SoC */`; `#define INTEL_PENTIUM_PRO IFM(6, 0x01)`; `#define INTEL_PENTIUM_II_KLAMATH IFM(6, 0x03)`; `#define INTEL_PENTIUM_III_DESCHUTES IFM(6, 0x05)`; `#define INTEL_PENTIUM_III_TUALATIN IFM(6, 0x0B)`; `#define INTEL_PENTIUM_M_DOTHAN IFM(6, 0x0D)`; `#define INTEL_CORE_YONAH IFM(6, 0x0E)`; `#define INTEL_CORE2_MEROM IFM(6, 0x0F)`; `#define INTEL_CORE2_MEROM_L IFM(6, 0x16)`; `#define INTEL_CORE2_PENRYN IFM(6, 0x17)`; `#define INTEL_CORE2_DUNNINGTON IFM(6, 0x1D)`; `#define INTEL_NEHALEM IFM(6, 0x1E)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_FAMILY_H`; `#define IFM(_fam, _model) VFM_MAKE(X86_VENDOR_INTEL, _fam, _model)`; `#define INTEL_ANY IFM(X86_FAMILY_ANY, X86_MODEL_ANY)`; `#define INTEL_FAM5_START IFM(5, 0x00) /* Notational marker, also P5 A-step */`; `#define INTEL_PENTIUM_75 IFM(5, 0x02) /* P54C */`; `#define INTEL_PENTIUM_MMX IFM(5, 0x04) /* P55C */`; `#define INTEL_QUARK_X1000 IFM(5, 0x09) /* Quark X1000 SoC */`; `#define INTEL_PENTIUM_PRO IFM(6, 0x01)`; `#define INTEL_PENTIUM_II_KLAMATH IFM(6, 0x03)`; `#define INTEL_PENTIUM_III_DESCHUTES IFM(6, 0x05)`; `#define INTEL_PENTIUM_III_TUALATIN IFM(6, 0x0B)`; `#define INTEL_PENTIUM_M_DOTHAN IFM(6, 0x0D)`; `#define INTEL_CORE_YONAH IFM(6, 0x0E)`; `#define INTEL_CORE2_MEROM IFM(6, 0x0F)`; `#define INTEL_CORE2_MEROM_L IFM(6, 0x16)`; `#define INTEL_CORE2_PENRYN IFM(6, 0x17)`; `#define INTEL_CORE2_DUNNINGTON IFM(6, 0x1D)`; `#define INTEL_NEHALEM IFM(6, 0x1E)`; `#define INTEL_NEHALEM_G IFM(6, 0x1F) /* Auburndale / Havendale */`; `#define INTEL_NEHALEM_EP IFM(6, 0x1A)`; `#define INTEL_NEHALEM_EX IFM(6, 0x2E)`; `#define INTEL_WESTMERE IFM(6, 0x25)`; `#define INTEL_WESTMERE_EP IFM(6, 0x2C)`; `#define INTEL_WESTMERE_EX IFM(6, 0x2F)`

## Control Flow
No runtime flow; constants encode CPUID family/model values for processors from legacy Core/Atom through modern server/client families.

## State and Persistence
State is absent; the header is a shared numeric ABI for CPUID matching.

## Dependencies and Integration Points
Depends on CPUID decoding users throughout arch/x86, drivers, perf, power, and security mitigation code.

## Risks
Risks include duplicate/wrong model numbers, missing aliases for steppings, and downstream quirks silently not applying.

## Test Signals
Tests should include compile coverage, CPUID matching on affected hardware, quirk unit checks where available, and review against Intel CPUID documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h -->
