## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/note.S

Purpose: includes common vDSO note metadata for the 64-bit image.

Important dependency: `#include "common/note.S"`.

Control flow: assembly inclusion emits version and build-salt notes.

State/persistence: embeds PT_NOTE metadata into 64-bit and x32-derived vDSO artifacts.

Integration points: vdso64 Makefile, common layout script, and ELF tooling.

Risks: include/layout errors affect vDSO metadata visibility. Test signals include readelf notes on `vdso64.so.dbg` and `vdsox32.so.dbg`.
