## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elfnote.h

Purpose: reserves PowerPC-specific ELF note type identifiers.

Important APIs/types/functions: `PPC_ELFNOTE_CAPABILITIES` identifies a PowerPC-named note containing a capabilities bitmap.

Control flow: constants only. Assembly note generation and tools consume the identifier.

State and persistence: ELF notes persist in the kernel image; this header owns no runtime state.

Dependencies and integration: integrates with `arch/powerpc/kernel/note.S` and boot/load tooling that inspects kernel capability notes.

Risks and test signals: note type collisions or format drift break external consumers. Test signals include readelf inspection of kernel notes and tooling that parses PowerPC capability notes.
