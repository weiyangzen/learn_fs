## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_async_events.h

Purpose: Goya asynchronous event ID enumeration. It defines firmware/hardware event numbers from PCIe, TPC, MME, MMU, DMA, DDR, SRAM, PLL, PSOC, GPIO, thermal/power, queue, and driver-control domains, ending with `GOYA_ASYNC_EVENT_ID_LAST_VALID_ID = 1023` and `GOYA_ASYNC_EVENT_ID_SIZE`.

Important API surface: `enum goya_async_event_id` values are stable protocol IDs. Notable grouped ranges include TPC ECC (`36..57` step 3), TPC decoder (`117..138` step 3), PLL0-6 (`143..149`), TPC BMON/kernel errors (`190..261` step 10 per TPC), DMA channels, DDR0/DDR1 ECC and AXI events, TPC CMDQ/QM ranges (`430..445`), DMA QM/channel ranges (`449..459`), and control events such as `PI_UPDATE`, `HALT_MACHINE`, `SOFT_RESET`, and environment fix start/end.

Control flow and state: no functions, but `goya.c` switches over these IDs, increments `events_stat` and `events_stat_aggregate`, maps ranges to engine indices, and selects severity/reset handling.

Dependencies and integration: included by `goyaP.h`; array sizes in `struct goya_device` use `GOYA_ASYNC_EVENT_ID_SIZE`; user/debug reporting returns these stats.

Risks and test signals: changing IDs breaks firmware-driver ABI and event decoding. Test with firmware event injection, range-index calculations, bounds checking for invalid IDs, event-stat reporting, and reset/escalation policy coverage.
