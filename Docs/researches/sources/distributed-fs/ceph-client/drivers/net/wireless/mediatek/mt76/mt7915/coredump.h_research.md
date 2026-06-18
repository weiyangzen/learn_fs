# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.h

Purpose: Data contract and conditional API declarations for MT7915 firmware coredumps.

Important types: `struct trace`, `struct mt7915_coredump`, `struct mt7915_coredump_mem`, `struct mt7915_mem_hdr`, and `struct mt7915_mem_region`. Public functions are declared when `CONFIG_DEV_COREDUMP` is enabled; otherwise inline stubs return benign defaults.

Control flow: no runtime flow in the header. It defines the packed binary format consumed by `coredump.c` and allows `init.c`/`mac.c` to call coredump APIs unconditionally.

State and persistence: the packed dump format persists in devcoredump output. It includes magic, length, GUID, wall-clock time, kernel and firmware versions, device id, firmware state, trace indices, sched/irq traces, task queue/stack info, context, call stack, and flexible memory data.

Dependencies and integration: includes `mt7915.h`, uses `guid_t`, ethtool firmware version length, and chip-specific crash data from the main device structure.

Risks: packed layout is an ABI for debugging tools; field reordering or size changes can break parsers. Flexible arrays require careful allocation math. Stub behavior means callers cannot infer coredump availability from successful register/submit return alone when the feature is compiled out.

Test signals: compile with and without `CONFIG_DEV_COREDUMP`, static layout/size expectations for parsers, successful no-op behavior with stubs, and dump parser validation against real crash artifacts.
