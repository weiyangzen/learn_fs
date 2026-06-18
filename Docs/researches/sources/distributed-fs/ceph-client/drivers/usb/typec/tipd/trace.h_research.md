# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.h

Purpose: Declares the TPS6598x tracepoint set and readable decoders for controller interrupt, status, power, and data-status bitfields, including generic TPS6598x, Apple CD321x, and TPS25750 variants.

Important APIs/types/functions: macros such as `show_irq_flags`, `show_cd321x_irq_flags`, `show_tps25750_irq_flags`, `show_status_*`, `show_power_status_*`, and `show_data_status_*` feed `TP_printk`. Trace events include `tps6598x_irq`, `cd321x_irq`, `tps25750_irq`, `tps6598x_status`, `tps25750_status`, `tps6598x_power_status`, `tps25750_power_status`, `tps6598x_data_status`, and `cd321x_data_status`.

Control flow and state: no stateful runtime logic; generated tracepoint code records event arguments from driver call sites and formats them through symbolic/flag decoders.

Persistence behavior: none. The tracing subsystem owns event enablement and buffering.

Dependencies/integration points: includes `tps6598x.h` so trace decoding uses the same masks as the driver. The header follows the kernel trace pattern with `TRACE_INCLUDE_FILE trace`, `TRACE_INCLUDE_PATH .`, and final inclusion of `<trace/define_trace.h>`.

Risks: trace formatting can become misleading if masks diverge from hardware or from `core.c` behavior. Because trace headers are sensitive to include guards and `TRACE_HEADER_MULTI_READ`, accidental restructuring can break tracepoint generation.

Test signals: compile with `CONFIG_TRACING`, enable each event under tracefs, and exercise IRQ, plug, power-status, TPS25750 charger-detect, DP, TBT, USB4, and CD321x HPD/data-status paths to confirm names and decoded fields are intelligible.
