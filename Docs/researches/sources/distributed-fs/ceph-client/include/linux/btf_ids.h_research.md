## sources/distributed-fs/ceph-client/include/linux/btf_ids.h

**Purpose:** This header defines compile/link-time machinery for collecting symbolic BTF IDs into the `.BTF_ids` ELF section and later resolving them with `resolve_btfids`.

**Important APIs/types/functions:** `struct btf_id_set` stores a count and sorted `u32` IDs. `struct btf_id_set8` stores count, flags, and `{ id, flags }` pairs. Macros include `BTF_ID`, `BTF_ID_FLAGS`, `BTF_ID_LIST`, `BTF_ID_LIST_GLOBAL`, `BTF_ID_UNUSED`, `BTF_SET_START/END`, `BTF_SET8_START/END`, and `BTF_KFUNCS_START/END`. `BTF_SET8_KFUNCS` marks kfunc sets.

**Control flow, state, persistence:** With `CONFIG_DEBUG_INFO_BTF`, macros emit assembler objects into `.BTF_ids`; the IDs are initially zero and resolved at link/post-link time. Without BTF debug info, the macros become static dummy arrays/sets so code still compiles without runtime ID content.

**Dependencies/integration:** Depends on compiler attributes, stringification, inline asm, and the external `resolve_btfids` tool. It is consumed by BPF/kfunc code and queried through helpers in `btf.h`.

**Risks and test signals:** Risks are layout changes not mirrored in `resolve_btfids`, using unsorted sets where binary search is expected, missing debug BTF config, and duplicate or unused entries. Test signals are successful `resolve_btfids` runs, BPF selftests that locate expected IDs, module builds with and without `CONFIG_DEBUG_INFO_BTF`, and objdump checks for `.BTF_ids`.
