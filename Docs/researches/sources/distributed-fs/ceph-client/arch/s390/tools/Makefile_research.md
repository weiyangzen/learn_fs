<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/tools/Makefile

Purpose: This Makefile builds s390 host tools and generated architecture headers for facility masks, disassembler opcode tables, and relocation data.

Important APIs/types/functions: It defines generated headers `arch/s390/include/generated/asm/facility-defs.h` and `dis-defs.h`, host programs `gen_facilities`, `gen_opcode_table`, and `relocs`, filechk commands for generated header content, and phony targets `kapi` and `relocs`.

Control flow: The `kapi` target depends on generated headers. `facility-defs.h` is produced by running `gen_facilities`; `dis-defs.h` runs `gen_opcode_table` with `opcodes.txt` as input. The `relocs` phony target ensures the host relocation scanner is built.

State and persistence: Generated headers persist under the generated asm include directory and are consumed by s390 kernel builds. Host tools are build artifacts.

Dependencies and integration points: It depends on Kbuild hostprogs, Linux include paths for `gen_facilities`, `opcodes.txt`, and s390 build stages that need generated headers before compiling the kernel/disassembler.

Risks and test signals: Generated header changes affect instruction decoding and CPU facility masks. Filechk output must be deterministic. Tests include clean builds, incremental rebuilds when tools/opcodes change, generated-header diff review, and host compiler portability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/Makefile -->
