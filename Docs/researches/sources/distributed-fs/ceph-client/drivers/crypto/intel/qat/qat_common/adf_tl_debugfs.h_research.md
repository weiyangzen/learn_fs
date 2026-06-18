# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.h

Purpose: defines telemetry debugfs counter names, offset-building macros, counter descriptor types, aggregation value type, and debugfs lifecycle declarations.

Important types/macros: counter name constants define user-visible report keys. `ADF_TL_*_REG_OFF` macros compute offsets into generation-specific telemetry layout structs. `enum adf_tl_counter_type` selects simple, ns, average-latency, or Mbps formatting. `struct adf_tl_dbg_counter` describes one counter's name/type/offsets. `ADF_TL_COUNTER` and `ADF_TL_COUNTER_LATENCY` build descriptors. `struct adf_tl_dbg_aggr_values` stores current/min/max/avg.

Control flow and state: header only. Descriptor arrays are Gen-specific static data, and runtime values come from `adf_telemetry`.

Dependencies and integration: used by Gen6 telemetry metadata and `adf_tl_debugfs.c`.

Risks and test signals: offset macros depend on exact naming of generation layout structs and members. Test compile coverage for each generation, stable debugfs key names, and formatting behavior for every counter type.
