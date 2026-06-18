# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-mem-types.h

Purpose: defines memory accounting IDs for thin-arbiter allocations.

Important APIs/types: `gf_ta_mem_types_t` starts at `gf_common_mt_end + 1` and defines `gf_ta_mt_local_t`, `gf_ta_mt_char`, and `gf_ta_mt_end`.

Control flow/state: no executable behavior. The enum is expected to be passed to thin-arbiter memory accounting initialization and allocation calls.

Dependencies/integration: includes `glusterfs/mem-types.h` and is included by thin-arbiter implementation/header files.

Risks/test signals: allocation tags must stay synchronized with implementation use. Tests should cover mem accounting initialization and compile checks when adding new thin-arbiter allocation classes.
