# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.h

## Purpose
This header provides the public initialization declaration for ARM64 KVM hyp tracing, with a stub when nVHE EL2 tracing is disabled.

## Important APIs, Types, and Functions
- `kvm_hyp_trace_init()` is declared when `CONFIG_NVHE_EL2_TRACING` is enabled.
- A static inline no-op returning `0` is provided otherwise.

## Control Flow
There is no runtime control flow beyond compile-time selection. Callers can invoke `kvm_hyp_trace_init()` unconditionally and receive either real initialization or a successful no-op depending on configuration.

## State and Persistence
The header holds no state. It gates access to state managed by `hyp_trace.c`.

## Dependencies and Integration Points
It is included by ARM64 KVM initialization code that wants optional hyp tracing without scattering `#ifdef CONFIG_NVHE_EL2_TRACING` checks.

## Risks and Edge Cases
The main risk is mismatched configuration: code may appear to initialize tracing but receive a no-op if the config is disabled. The include guard prevents duplicate declarations.

## Test Signals
Build with `CONFIG_NVHE_EL2_TRACING=y` and disabled. The enabled build should link `hyp_trace.c`; the disabled build should compile callers against the inline stub.
