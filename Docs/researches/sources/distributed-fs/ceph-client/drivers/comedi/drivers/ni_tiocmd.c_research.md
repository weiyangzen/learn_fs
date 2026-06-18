## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tiocmd.c

### Purpose
`ni_tiocmd.c` adds asynchronous Comedi command support for NI general-purpose counters, intentionally split from `ni_tio.c` so the base counter library does not depend directly on the MITE DMA module.

### Important APIs, Types, And Functions
Exported APIs are `ni_tio_cmd()`, `ni_tio_cmdtest()`, `ni_tio_cancel()`, `ni_tio_acknowledge()`, `ni_tio_handle_interrupt()`, and `ni_tio_set_mite_channel()`. Internal helpers include `ni_tio_configure_dma()`, `ni_tio_input_inttrig()`, `ni_tio_input_cmd()`, `ni_tio_output_cmd()`, `ni_tio_cmd_setup()`, `should_ack_gate()`, and `ni_tio_acknowledge_and_confirm()`.

### Control Flow, State, And Persistence
`ni_tio_cmdtest()` validates Comedi trigger combinations: start can be now/internal/other and optionally external on hardware with counting-mode registers; scan or convert may use external gate sources; stop is unsupported beyond `TRIG_NONE`. `ni_tio_cmd()` requires a bound MITE channel, configures an external gate if requested, enables gate interrupts for `CMDF_WAKE_EOS`, then starts input DMA or rejects output commands as unsupported. Input setup allocates the full buffer, prepares DMA width by variant, configures read acknowledge/interrupt bits, arms DMA immediately or installs an internal trigger callback. Cancellation disarms the counter, disarms DMA, disables DMA register bits, and clears gate interrupt enable.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `ni_tio_internal.h`, `mite.h`, and `ni_routes.h`. It integrates with board interrupt handlers that call `ni_tio_handle_interrupt()` and with callers that assign DMA channels through `ni_tio_set_mite_channel()`. Risks include no interrupt-only command path, unsupported output commands, E-series gate-ack behavior depending on DMA completion, commented-out external start-trigger validation, and ordering between MITE DMA arm/disarm and counter arm. Test signals include command validation steps, `TRIG_INT` start, external gate routing by raw and named routes, DMA overflow/DRQ error callbacks, gate/TC error reporting, `CMDF_WAKE_EOS`, and cancel while DMA is active.
