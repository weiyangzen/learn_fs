# sources/distributed-fs/ceph-client/arch/mips/boot/ecoff.h

Purpose: local ECOFF format definitions used by the MIPS `elf2ecoff` host conversion tool.

Important APIs and types: defines `FILHDR`, `SCNHDR`, and `AOUTHDR` structures plus ECOFF magic numbers, header sizes, section rounding, and offset macros such as `N_TXTOFF` and `N_DATOFF`.

Control flow: no executable control flow. `elf2ecoff.c` includes this header when constructing ECOFF headers from ELF load segments.

State and persistence: no runtime state; it describes on-disk binary layout emitted by the conversion utility.

Dependencies and integration points: depends on fixed-width integer types and historical MIPS ECOFF conventions.

Risks and test signals: structure layout or offset macro errors corrupt generated ECOFF images. Test by converting known ELF images, inspecting header fields, and booting firmware that consumes ECOFF.
