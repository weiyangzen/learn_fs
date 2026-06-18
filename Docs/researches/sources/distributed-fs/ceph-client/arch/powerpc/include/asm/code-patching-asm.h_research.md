## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/code-patching-asm.h

Purpose: provides an assembler macro for declaring patchable instruction sites.

Important APIs/types/functions: `patch_site label name` emits a global symbol in `.rodata` whose value is a 32-bit relative offset from the table location to the patch label.

Control flow: assembly-only metadata emission. The macro pushes `.rodata`, aligns to four bytes, defines `name`, writes `label - .`, and returns to the previous section.

State and persistence: the generated relative offset persists in the kernel image and is consumed by runtime patching code. The header owns no mutable state.

Dependencies and integration: integrates with PowerPC code-patching and alternative/fixup paths that need compact, relocatable patch-site descriptors.

Risks and test signals: offset width and section placement must match the patching consumer. Bad alignment or a stale symbol name can make boot-time patching corrupt code. Test signals are assembler builds, objdump inspection of patch-site tables, boot-time code patching, ftrace/static-call style patch users, and module/vDSO relocation coverage where applicable.
