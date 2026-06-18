# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-auxadc.c

`wm831x-auxadc.c` implements raw and microvolt AUXADC reads for WM831x PMICs. It chooses an interrupt-backed queued conversion path when a chip IRQ exists and a serialized polled path otherwise.

Important pieces are `struct wm831x_auxadc_req`, `wm831x_auxadc_read_irq()`, `wm831x_auxadc_irq()`, `wm831x_auxadc_read_polled()`, exported `wm831x_auxadc_read()`, exported `wm831x_auxadc_read_uv()`, and `wm831x_auxadc_init()`. IRQ mode queues a request on `wm831x->auxadc_pending`, enables the source and converter, waits up to 500 ms for completion, and returns the value stored by the IRQ handler. The handler reads `WM831X_AUXADC_DATA`, decodes source, disables the completed source, powers off the ADC if no sources remain active, and completes all matching pending requests. Polled mode starts one source, sleeps 20 ms, checks and acknowledges `WM831X_AUXADC_DATA_EINT`, validates the returned source, and returns masked raw data.

Persistent state is in `wm831x->auxadc_lock`, `auxadc_pending`, `auxadc_active`, and `auxadc_read`; hardware state is the AUXADC control/source/data and interrupt status registers. Dependencies include WM831x core register helpers, IRQ mapping via `wm831x_irq()`, Linux completions/lists, and AUXADC register definitions.

Risks: this source uses `kzalloc_obj(*req)`, which must exist in the target tree; timeout is represented by the request's initial `-ETIMEDOUT`; cleanup writes in the IRQ handler ignore errors; polled mode depends on a fixed 20 ms delay. Test signals are successful build, reads with and without IRQ, concurrent same-channel/different-channel reads, microvolt conversion checks, and injected regmap failures.
