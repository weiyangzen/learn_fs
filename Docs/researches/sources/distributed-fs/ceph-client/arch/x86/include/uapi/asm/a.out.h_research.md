<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h

Purpose: Exposes the legacy x86 `a.out` executable header layout and size accessor macros for userspace and compatibility tools.

Important APIs/types/functions: `struct exec`, `N_TRSIZE()`, `N_DRSIZE()`, and `N_SYMSIZE()`.

Control flow: No executable flow. Loaders or file-inspection tools read `struct exec` fields and use the macros to locate relocation and symbol data.

State and persistence behavior: No runtime state. It preserves on-disk ABI field order for old `a.out` binaries.

Dependencies and integration points: Integrated with legacy binary-format tooling and any compatibility loader code that still parses x86 `a.out`.

Risks and test signals: Risks are layout changes or macro incompatibility for old tools. Test by compiling userspace that includes the header and by parsing known `a.out` fixtures if legacy support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h -->
