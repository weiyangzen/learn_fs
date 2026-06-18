
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_sys-t.c

Purpose: MIPI SyS-T framing protocol driver for STM. It wraps STM payloads with SyS-T headers, GUIDs, optional length/timestamps, optional clock sync messages, and ftrace-compatible Structured Binary Data framing.

Important APIs/types/functions: enums and macros encode SyS-T message type/severity/subtype/option fields. `struct sys_t_policy_node` stores per-policy UUID and interval settings. `struct sys_t_output` snapshots policy settings per output and tracks jiffies for periodic metadata. Configfs attributes expose `uuid`, `do_len`, `ts_interval`, and `clocksync_interval`. `sys_t_write()` is the protocol write path; helpers include `sys_t_clock_sync()`, `sys_t_header()`, and `sys_t_write_data()`.

Control flow: protocol registration provides private policy-node storage and output open/close callbacks. Policy-node creation generates a UUID by default. Output open copies policy settings into per-output private data. Each write may first emit a clock-sync frame if due, builds a SyS-T header from source type and options, emits timestamped header, GUID, optional length, optional timestamp, payload data, and final FLAG. Ftrace sources are treated specially by converting the first 64 bits to a SyS-T SBD ID64-compatible header before sending remaining data.

State and persistence: policy values live in configfs objects while the policy exists; per-output private state is allocated on channel assignment and freed on output close. Jiffies timestamps throttle periodic SyS-T metadata. No on-disk persistence beyond userspace-created configfs state.

Dependencies and integration: depends on STM protocol driver API, configfs merged policy attributes, UUID helpers, ktime, jiffies, and STM source type values.

Risks: interval attributes are copied at output-open time, so later policy changes may not affect already assigned outputs. Ftrace compatibility assumes minimum buffer length and bit layout. `u16 length = count` truncates payload lengths above 65535 when `do_len` is enabled. Metadata insertion can alter bandwidth and timing.

Test signals: create `p_sys-t` policy, inspect/change configfs attributes, write normal and ftrace sources, verify GUID/header/FLAG layout, test length option with large payloads, test timestamp and clock-sync intervals, and unload after output close.
