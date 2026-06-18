# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.c

Purpose: implements Intel GMBUS/DDC I2C adapters, including platform pin maps, hardware GMBUS transfers, GPIO bit-banging fallback, HDCP Aksv output, power-domain handling, bus locking, IRQ wakeups, and setup/teardown.

Important APIs/types/functions: private `struct intel_gmbus` embeds `i2c_adapter`, force-bit state, `reg0`, GPIO register, bit-bang algorithm data, and display pointer. Public functions include `intel_gmbus_setup()`, `intel_gmbus_teardown()`, `intel_gmbus_get_adapter()`, `intel_gmbus_is_valid_pin()`, `intel_gmbus_force_bit()`, `intel_gmbus_is_forced_bit()`, `intel_gmbus_reset()`, `intel_gmbus_output_aksv()`, and `intel_gmbus_irq_handler()`. Internal transfer helpers implement wait, idle wait, read/write chunks, index transfers, retry, stop cycles, error clearing, and pin GPIO operations.

Control flow: setup selects MMIO base, initializes mutex/waitqueue, creates one adapter per valid platform pin, wires hardware and bit-bang algorithms, and registers adapters. `gmbus_xfer()` takes the GMBUS power domain, uses bit-banging if forced or after prior timeout, otherwise runs hardware transfers. Hardware transfer programs GMBUS0, combines index messages when possible, handles chunked reads/writes and burst-read override, waits for ready/wait/idle, emits STOP, clears NAK/errors, retries first NAK once, and falls back to bit-banging with `-EAGAIN` on timeout. GPIO fallback resets GMBUS, handles clock-gating workarounds, sets open-drain lines, and preserves required mask/pull-up bits.

State and persistence: `display->gmbus.bus[]` stores adapters; each adapter persists until teardown. `force_bit` is a counter plus retry flag; `reg0` stores pin/rate. `display->gmbus.mutex`, waitqueue, and `mmio_base` persist for device lifetime. GMBUS controller and GPIO line state persist in MMIO registers across transfers until reset or reprogramming.

Dependencies and integration: integrates with Linux I2C core, i2c-algo-bit, DRM HDCP helper, i915 display power domains, IRQ enable state, display workarounds, PCH/platform pin maps, and `intel_gmbus_regs.h`.

Risks: GMBUS hardware only handles one interrupt-enable bit, so wait logic must poll NAKs. Returning `-ENXIO` too eagerly can suppress EDID retries; timeouts should fall back to bit-banging. Force-bit counter underflow is possible if callers unbalance requests. Pin maps vary by PCH/platform. Clock-gating and GPIO mask workarounds are transfer-critical.

Test signals: EDID/DDC reads across VGA/HDMI/DP/Type-C pins, long burst reads including 512-byte special case, indexed transfers, NAK and timeout injection, bit-bang fallback, HDCP Aksv write, adapter setup/teardown, IRQ wakeups, power-domain balance, and platform pin validation.
