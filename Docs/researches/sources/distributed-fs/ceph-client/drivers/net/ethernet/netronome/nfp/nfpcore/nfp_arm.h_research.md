# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_arm.h

Purpose: Defines ARM island memory-space offsets, GCSR register offsets, and bitfield helper macros for ARM-side BAR and explicit CPP access configuration.

Important APIs/types/functions: Key macro groups include `NFP_ARM_GCSR_BULK_BAR`, `NFP_ARM_GCSR_EXPA_BAR`, `NFP_ARM_GCSR_EXPL[0-2]_BAR`, `NFP_ARM_GCSR_EXPL_POST`, `NFP_ARM_GCSR_*_CSR()` composers, and fixed sizes such as `NFP_ARM_GCSR_SIZE`, `NFP_ARM_MPCORE_SIZE`, and `NFP_ARM_PCSR_SIZE`.

Control flow/state: Header-only register definitions. Runtime users compose CSR values and decode fields; this file does not allocate or mutate state directly.

Dependencies/integration: Used by CPP core/model detection and any ARM-interface CPP implementation. It shares the same CPP target/action/token semantics as `nfp_cpp.h` and NFP6000 register definitions.

Risks: Bitfield macros directly encode hardware ABI. A wrong shift/mask can route accesses to the wrong target or corrupt explicit transaction setup. Since many macros use plain integer shifts, callers must provide already-sanitized values.

Test signals: Build tests catch syntax only; hardware tests should verify ARM GCSR reads, model autodetection, explicit transaction setup, and BAR CSR composition against known-good hardware traces.
