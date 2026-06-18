<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h

Purpose: Adds PowerPC architecture feature strings to module vermagic so modules are tied to compatible kernel instrumentation/relocation settings.

Important APIs/types/functions: `MODULE_ARCH_VERMAGIC_FTRACE`, `MODULE_ARCH_VERMAGIC_RELOCATABLE`, and combined `MODULE_ARCH_VERMAGIC`.

Control flow: Preprocessor selects strings for patchable-function-entry, mprofile-kernel, relocatable kernels, or empty alternatives; module build embeds the concatenated string.

State and persistence: No runtime state. The resulting module metadata persists in built `.ko` files and participates in module loading compatibility checks.

Dependencies and integration points: Driven by `CONFIG_ARCH_USING_PATCHABLE_FUNCTION_ENTRY`, `CONFIG_MPROFILE_KERNEL`, and `CONFIG_RELOCATABLE`; consumed by Linux module infrastructure.

Risks: Missing a configuration bit can allow incompatible modules to load or reject compatible modules unnecessarily.

Test signals: Build modules under each tracing/relocation configuration and verify `modinfo vermagic` plus module load/reject behavior.

Source read size: 22 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vermagic.h -->
