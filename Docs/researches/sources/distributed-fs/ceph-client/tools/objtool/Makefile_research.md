# sources/distributed-fs/ceph-client/tools/objtool/Makefile

Purpose: host-build Makefile for Linux `objtool`. It configures architecture capabilities, optional ORC/KLP/disassembler support, libsubcmd dependency builds, and final host linking.

Important variables/control flow: includes shared make helpers and arch detection. x86 enables ORC and livepatch capability; loongarch enables ORC. If livepatch is supported, it probes `libxxhash` by compiling a small program and enables `BUILD_KLP` plus flags/libs on success. It computes `srctree`, `LIBSUBCMD_OUTPUT`, `OBJTOOL`, `OBJTOOL_IN`, libelf flags/libs, warning flags, include paths, and host overrides. It probes old libelf `elf_getshdr` needs, libopcodes link combinations, and styled disassembler support.

Build targets: `all` builds `$(OBJTOOL)`. `$(OBJTOOL_IN)` depends on `fixdep`, `libsubcmd`, and `FORCE`, runs `sync-check.sh`, and delegates object build through `tools/build/Makefile.include`. The final link uses `HOSTCC`. `$(LIBSUBCMD)` builds and installs libsubcmd headers into its output. `clean` removes object/dependency/cmd files plus generated arch/helper files; `mrproper` also removes the binary.

State/dependencies: persists build artifacts under `OUTPUT` or current directory, exports feature variables to sub-makes, and depends on host pkg-config, libelf, optional xxhash/libopcodes/binutils headers.

Risks/test signals: feature probes are host-environment sensitive. Static libopcodes dependency order can fail on uncommon distros. Clean uses `find $(OUTPUT)` and can behave poorly if `OUTPUT` is empty or unexpected. Signals include successful host build across supported arches and correct `BUILD_ORC`, `BUILD_KLP`, and `BUILD_DISAS` exports.
