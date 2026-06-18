# sources/distributed-fs/ceph-client/arch/mips/boot/elf2ecoff.c

Purpose: host utility that converts a MIPS ELF kernel image into ECOFF format for firmware or boot paths that require ECOFF.

Important APIs and functions: `copy()` transfers file ranges. `combine()` merges adjacent/overlapping ELF load segments. `phcmp()` sorts program headers by virtual address. `saveRead()` reads checked file regions. Endian conversion helpers adjust ELF and ECOFF headers. `main()` parses input/output arguments, reads ELF headers/program headers, filters loadable segments plus MIPS metadata, computes ECOFF section/a.out headers, and writes the converted image.

Control flow: the tool opens the ELF, validates header shape, sorts program headers, combines text/data regions with padding/alignment, emits ECOFF file/header/section records, then copies segment payloads to their ECOFF offsets.

State and persistence: reads one input file and writes one output file. All conversion state is in process memory.

Dependencies and integration points: built as a host-side MIPS boot tool and depends on standard C/POSIX APIs, `<elf.h>`, network byte-order helpers, and local `ecoff.h` structures.

Risks and test signals: malformed ELF inputs, endian mismatch, segment overlap, and 32-bit size truncation can produce unbootable images. Test with known kernel ELF fixtures, `readelf`/hexdump inspection, firmware boot tests, and both big- and little-endian MIPS builds.
