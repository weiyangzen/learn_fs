## sources/distributed-fs/ceph-client/arch/arm64/include/asm/esr.h

Purpose: defines ESR_ELx exception class and syndrome field encodings plus helpers for decoding faults and traps.

Important APIs/types/functions: exports EC constants for traps, aborts, SError, BRK, SVE/SME/GCS/MOPS/PAuth/BTI, ISS/ISS2 masks, abort FSC helpers, system-instruction decoding macros, BRK comment masks, `esr_sys64_to_sysreg`, `esr_cp15_to_sysreg`, GCS/MOPS/SME fields, and inline helpers such as `esr_is_data_abort`, `esr_is_cfi_brk`, `esr_fsc_is_translation_fault`, and `esr_get_class_string`.

Control flow: handlers extract exception class and ISS fields, classify faults, convert trapped sysreg encodings, and decode sanitizer/control-flow breakpoints.

State and persistence: stateless decoding of exception syndrome values captured by hardware.

Dependencies and integration: used by exception handlers, KVM trap emulation, page fault handling, debug, CFI/UBSAN/KASAN, MTE, GCS, and user sysreg emulation.

Risks: wrong masks misclassify faults, send wrong signals, or emulate incorrect sysregs. Test signals are fault injection, KVM sysreg trap tests, sanitizer trap tests, MTE/GCS tests, and page-fault regression coverage.
