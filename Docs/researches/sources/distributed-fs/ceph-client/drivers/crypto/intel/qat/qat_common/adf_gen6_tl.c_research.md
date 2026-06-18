# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.c

Purpose: supplies Gen6 telemetry counter metadata consumed by the common telemetry debugfs code. It maps named counters to offsets inside the Gen6 firmware-populated telemetry DMA layout.

Important APIs: `adf_gen6_init_tl_data(struct adf_tl_hw_data *tl_data)` fills layout sizes, history depth, max monitored ring-pairs, conversion factors, counter arrays, and command-queue multipliers. Static counter tables cover device counters, slice utilization/execution counters, command queue wait/execute/drain counters, and ring-pair counters.

Control flow and state: mostly static data initialization. Runtime state is not stored here; `adf_tl_init/run` copies these descriptors into the hardware data path and uses them to interpret DMA snapshots.

Dependencies and integration: depends on `adf_gen6_tl.h` register layout structs, generic `adf_telemetry.h`, `adf_tl_debugfs.h` macros, and firmware admin slice-count structs. Integrated by Gen6 hardware-data setup before telemetry is initialized.

Risks and test signals: wrong offsets or queue multipliers produce misleading debugfs telemetry without obvious failures. Test by enabling telemetry, checking `device_data` and `rp_*_data` fields against firmware/hardware expectations, and verifying slice/cmdq counts do not exceed Gen6 maxima.
