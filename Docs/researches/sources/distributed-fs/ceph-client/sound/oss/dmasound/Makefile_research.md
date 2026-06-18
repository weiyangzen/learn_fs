# sources/distributed-fs/ceph-client/sound/oss/dmasound/Makefile

Purpose: Builds legacy OSS dmasound core plus the selected platform backend. It wires Atari, Amiga Paula, and Q40 config symbols to object lists.

Important APIs/types/functions: The three kbuild lines append `dmasound_core.o` plus `dmasound_atari.o`, `dmasound_paula.o`, or `dmasound_q40.o` according to `CONFIG_DMASOUND_ATARI`, `CONFIG_DMASOUND_PAULA`, or `CONFIG_DMASOUND_Q40`.

Control flow: Kbuild evaluates enabled `obj-*` entries. Each platform build includes its backend and a copy/link of the shared core object, producing the relevant built-in or module target under the OSS sound tree.

State and persistence: No runtime state. The build state determines which platform machine table implementation is linked with the dmasound core.

Dependencies/integration: Tied to `sound/oss/dmasound/Kconfig` and source files in the same directory. Risks include duplicate core linkage if multiple platform symbols are enabled in one build context, stale backend object names, and dependency drift between Kconfig and Makefile. Test signals are successful platform builds and resulting objects containing both core and backend symbols.
